# shared-kicad-lib
Shared Kicad Library with symbols, footprints, step files. Intended to be used as a seperate repo. Plans to be added as a submodule only after the project is ready for release/archive

## How To Import
If you have not already created a directory for git repos:
```bash
# On Bash / Terminal
cd ~
mkdir -p git
cd git
```
Navigate to your git repo (you are already in it if you did steps above)
```bash
# On Bash / Terminal
git clone git@github.com:ARCUIA/shared-kicad-lib.git
```
Now Open KiCad 10 (Do not use 9 unless you want to treat this as read-only)
```txt
# In Kicad
Preferences -> Configure Paths...
Hit '+' button bottom left
add 'SHARED_KICAD_LIB' with the path to your repo. Mine is: /home/sam/git/shared-kicad-lib/ for example.

Preferences -> Manage Symbol Libraries...
Hit '+' button bottom left
add 'Shared Kicad Lib' as nickname (do NOT include '')
add '${SHARED_KICAD_LIB}/sym-lib-table' as Library path (do NOT include '')
add 'Table' as library format
hit ok

Preferences -> Manage Footprint Libraries...
Hit '+' button bottom left
add 'Shared Kicad Lib' as nickname (do NOT include '')
add '${SHARED_KICAD_LIB}/fp-lib-table' as Library path (do NOT include '')
add 'Table' as library format
hit ok

```
You should now be able to use footprints provided in this repository.

Tutorial on adding symbols and footprints is 'coming soon'
