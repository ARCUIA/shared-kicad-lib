#!/usr/bin/env python3
"""Add a SnapMagic/SnapEDA zip (symbol + footprint + STEP) to the library.

    python3 scripts/add-part.py PART.zip [--name NAME] [--force] [--no-git]

NAME (default: the symbol's own name) becomes the symbol, the .pretty folder,
the .3dshapes folder and the STEP file name. The footprint keeps its own name.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def die(msg):
    sys.exit(f"error: {msg}")


def run(*cmd, **kw):
    subprocess.run(cmd, cwd=REPO, check=True, **kw)


def read(p):
    return p.read_bytes().decode("utf-8")


def write(p, s):
    p.write_bytes(s.encode("utf-8"))


def pick(root, exts, what):
    found = [p for p in root.rglob("*")
             if p.is_file() and p.suffix.lower() in exts
             and "__MACOSX" not in p.parts and not p.name.startswith("._")]
    if len(found) != 1:
        die(f"expected exactly 1 {what} in the zip, found {len(found)}: "
            f"{[p.name for p in found]}")
    return found[0]


def fix_symbol(sym, old, name, fp_name):
    if name != old:  # symbol + its _N_N unit sub-symbols, and the Value field
        sym = re.sub(r'\(symbol "' + re.escape(old) + r'(_\d+_\d+)?"',
                     lambda m: f'(symbol "{name}{m.group(1) or ""}"', sym)
        sym = re.sub(r'(\(property "Value" ")' + re.escape(old) + '"',
                     lambda m: f'{m.group(1)}{name}"', sym, count=1)
    sym, n = re.subn(r'(\(property "Footprint" ")[^"]*"',
                     lambda m: f'{m.group(1)}{name}:{fp_name}"', sym, count=1)
    if not n:
        print("warning: symbol has no Footprint property; link it manually")
    return sym


def fix_footprint(fp, name):
    path = f"${{SHARED_KICAD_LIB}}/3dmodels/{name}.3dshapes/{name}.STEP"
    if re.search(r'\(model\s', fp):  # repoint existing model, keep its offsets
        return re.sub(r'(\(model\s+)("[^"]*"|[^\s()]+)',
                      lambda m: f'{m.group(1)}"{path}"', fp)
    pos = "offset" if "(version" in fp else "at"  # new vs. legacy file format
    block = (f'  (model "{path}"\n'
             f'    ({pos} (xyz 0 0 0))\n'
             f'    (scale (xyz 1 1 1))\n'
             f'    (rotate (xyz 0 0 0))\n'
             f'  )\n')
    body = fp.rstrip()
    if not body.endswith(")"):
        die("footprint file is malformed")
    return body[:-1].rstrip() + "\n" + block + ")\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zip", type=Path)
    ap.add_argument("--name", help="name for symbol / .pretty / .3dshapes / STEP")
    ap.add_argument("--force", action="store_true", help="overwrite an existing part of the same name")
    ap.add_argument("--no-git", action="store_true", help="skip pull/commit/push")
    args = ap.parse_args()

    if not args.zip.is_file():
        die(f"{args.zip} not found")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(args.zip) as z:
            z.extractall(tmp)
        sym_src = pick(tmp, {".kicad_sym"}, "symbol (.kicad_sym)")
        fp_src = pick(tmp, {".kicad_mod"}, "footprint (.kicad_mod)")
        step_src = pick(tmp, {".step", ".stp"}, "STEP file")

        sym = read(sym_src)
        m = re.search(r'\(symbol "([^"]+)"', sym)
        if not m:
            die("no symbol found in .kicad_sym")
        old = m.group(1)
        name = args.name or old
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*", name):
            die(f"'{name}' isn't usable as a folder name; pass --name")

        if not args.no_git:
            run("git", "pull", "--rebase", "--autostash")

        sym_dst = REPO / "symbols" / f"{name}.kicad_sym"
        pretty = REPO / "footprints" / f"{name}.pretty"
        shapes = REPO / "3dmodels" / f"{name}.3dshapes"
        clash = [p for p in (sym_dst, pretty, shapes) if p.exists()]
        if clash and not args.force:
            die(f"{name} already exists ({', '.join(p.name for p in clash)}); "
                "use --force to overwrite or --name to pick another name")
        for p in clash:
            shutil.rmtree(p) if p.is_dir() else p.unlink()

        pretty.mkdir(parents=True)
        shapes.mkdir(parents=True)
        write(sym_dst, fix_symbol(sym, old, name, fp_src.stem))
        write(pretty / fp_src.name, fix_footprint(read(fp_src), name))
        shutil.copyfile(step_src, shapes / f"{name}.STEP")

    # same job the GitHub Action does; LC_ALL=C keeps the ordering identical to CI's
    run("bash", "scripts/generate-lib-tables.sh", env={**os.environ, "LC_ALL": "C"})

    if not args.no_git:
        run("git", "add", f"symbols/{name}.kicad_sym", f"footprints/{name}.pretty",
            f"3dmodels/{name}.3dshapes", "sym-lib-table", "fp-lib-table")
        run("git", "commit", "-m", f"Add {name}")
        run("git", "push")

    print(f"Added {name}: symbols/{name}.kicad_sym, footprints/{name}.pretty/{fp_src.name}, "
          f"3dmodels/{name}.3dshapes/{name}.STEP")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        die(f"command failed: {' '.join(map(str, e.cmd))}")
