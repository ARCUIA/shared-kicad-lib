#!/usr/bin/env python3
"""Register this repo with KiCad, no GUI clicking required.

Sets the SHARED_KICAD_LIB path variable and adds the 'Shared Kicad Lib' entry
to KiCad's global symbol and footprint library tables. Close KiCad first.

    python3 scripts/setup.py [--kicad-version 10.0] [--config-dir DIR]
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NICKNAME = "Shared Kicad Lib"
VAR = "SHARED_KICAD_LIB"


def die(msg):
    sys.exit(f"error: {msg}")


def find_config_dir(version):
    home = Path.home()
    system = platform.system()
    if system == "Darwin":
        candidates = [home / "Library/Preferences/kicad" / version]
    elif system == "Windows":
        candidates = [Path(os.environ.get("APPDATA", home)) / "kicad" / version]
    else:
        xdg = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config")
        candidates = [
            xdg / "kicad" / version,
            home / ".var/app/org.kicad.KiCad/config/kicad" / version,  # Flatpak
        ]
    for c in candidates:
        if c.is_dir():
            return c
    die(f"no KiCad {version} config dir found (looked in: "
        f"{', '.join(map(str, candidates))}). Launch KiCad {version} once, "
        "or pass --config-dir.")


def kicad_running():
    try:
        return subprocess.run(["pgrep", "-x", "kicad"], capture_output=True).returncode == 0
    except FileNotFoundError:  # no pgrep (Windows)
        return False


def backup(f):
    """Keep one pristine copy of anything we modify."""
    bak = f.with_name(f.name + ".bak")
    if f.exists() and not bak.exists():
        shutil.copy2(f, bak)


def set_path_var(config_dir):
    f = config_dir / "kicad_common.json"
    data = json.loads(f.read_text()) if f.exists() else {}
    env = data.setdefault("environment", {})
    if not isinstance(env.get("vars"), dict):  # KiCad writes null when empty
        env["vars"] = {}
    value = REPO.as_posix()
    if env["vars"].get(VAR) == value:
        return "already set"
    backup(f)
    env["vars"][VAR] = value
    f.write_text(json.dumps(data, indent=4) + "\n")
    return "set"


def add_table_entry(config_dir, table, root_tag):
    f = config_dir / table
    if not f.exists():
        die(f"{f} not found. Launch KiCad once so it creates its default tables.")
    text = f.read_text()
    if not text.lstrip().startswith(f"({root_tag}"):
        die(f"{f} doesn't look like a {root_tag}; not touching it.")
    if f'(name "{NICKNAME}")' in text:
        return "already present"
    entry = (f'  (lib (name "{NICKNAME}")(type "Table")'
             f'(uri "${{{VAR}}}/{table}")(options "")(descr ""))\n')
    body = text.rstrip()
    if not body.endswith(")"):
        die(f"{f} is malformed; not touching it.")
    backup(f)
    f.write_text(body[:-1].rstrip() + "\n" + entry + ")\n")
    return "added"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--kicad-version", default="10.0")
    ap.add_argument("--config-dir", type=Path, help="KiCad settings dir (auto-detected by default)")
    args = ap.parse_args()

    for t in ("sym-lib-table", "fp-lib-table"):
        if not (REPO / t).exists():
            die(f"{REPO / t} missing; run: bash scripts/generate-lib-tables.sh")
    if kicad_running():
        die("KiCad is running; close it first (it would overwrite these changes on exit).")

    config_dir = args.config_dir or find_config_dir(args.kicad_version)
    print(f"KiCad config: {config_dir}")
    print(f"{VAR} = {REPO.as_posix()}: {set_path_var(config_dir)}")
    print(f"sym-lib-table: {add_table_entry(config_dir, 'sym-lib-table', 'sym_lib_table')}")
    print(f"fp-lib-table:  {add_table_entry(config_dir, 'fp-lib-table', 'fp_lib_table')}")
    print("Done. Start KiCad.")


if __name__ == "__main__":
    main()
