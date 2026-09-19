#!/usr/bin/env bash
# generate-lib-tables.sh
# Run from inside club-kicad-lib. Writes fp-lib-table / sym-lib-table
# directly into this repo, referenced by ${CLUB_KICAD_LIB} for the
# separate-clone approach (nested "Table" type in global config).
set -e

{
  echo "(sym_lib_table"
  echo "        (version 7)"
  for f in symbols/*.kicad_sym; do
    [ -e "$f" ] || continue
    n=$(basename "$f" .kicad_sym)
    echo "        (lib (name \"$n\")(type \"KiCad\")(uri \"\${CLUB_KICAD_LIB}/symbols/$n.kicad_sym\")(options \"\")(descr \"\"))"
  done
  echo ")"
} > sym-lib-table

{
  echo "(fp_lib_table"
  echo "        (version 7)"
  for d in footprints/*.pretty; do
    [ -e "$d" ] || continue
    n=$(basename "$d" .pretty)
    echo "        (lib (name \"$n\")(type \"KiCad\")(uri \"\${CLUB_KICAD_LIB}/footprints/$n.pretty\")(options \"\")(descr \"\"))"
  done
  echo ")"
} > fp-lib-table

echo "Wrote sym-lib-table ($(ls symbols/*.kicad_sym 2>/dev/null | wc -l) libs) and fp-lib-table ($(ls -d footprints/*.pretty 2>/dev/null | wc -l) libs)."
