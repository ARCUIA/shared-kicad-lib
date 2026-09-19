cd ~/git/shared-kicad-lib
find footprints -name "*.kicad_mod" | while read -r mod; do
  name=$(basename "$(dirname "$mod")" .pretty)
  sed -i -E "s#\(model \"[^\"]*\"#(model \"\${SHARED_KICAD_LIB}/3dmodels/${name}.3dshapes/${name}.STEP\"#" "$mod"
done
