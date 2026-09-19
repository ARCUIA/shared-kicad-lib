cd ~/git/shared-kicad-lib/

echo "== Renaming .step -> .STEP =="
find 3dmodels -iname "*.step" | while read -r f; do
  # skip files that are already correctly-cased .STEP
  case "$f" in
    *.STEP) continue ;;
  esac
  newname="${f%.*}.STEP"
  echo "  $f -> $newname"
  mv "$f" "$newname"
done

echo "== Fixing any footprint references still pointing at lowercase .step =="
find footprints -name "*.kicad_mod" | while read -r mod; do
  if grep -q '\.step"' "$mod"; then
    sed -i 's/\.step"/.STEP"/' "$mod"
    echo "  fixed reference in: $mod"
  fi
done

echo "Done."
