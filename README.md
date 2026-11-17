# shared-kicad-lib
Shared Kicad Library with symbols, footprints, step files. Intended to be used as a seperate repo. Plans to be added as a submodule only after the project is ready for release/archive

## How To Setup
```bash
# On Bash / Terminal
mkdir -p ~/git && cd ~/git
git clone git@github.com:ARCUIA/shared-kicad-lib.git
cd shared-kicad-lib
python3 scripts/setup.py   # close KiCad first
```

## How To Automatically Add New Symbol (Directly From Zip)
- Tested on Snapmagic zip file

```bash
# First download part zip from Snapmagic to download directory
# Now On Bash / Terminal:
python3 scripts/add-part.py ~/Downloads/PART.zip              # names taken from the symbol
------- OR -------------------
python3 scripts/add-part.py ~/Downloads/PART.zip --name PART  # if you want custom name different from the existing name

# You may now delete the zip file, and folder in download directory.
```

## How To Update From Remote
```bash
# On Bash / Terminal
cd ~/git/shared-kicad-lib
git pull
exit
```



---
Perform these steps if the setup.py script failed
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
You should now be able to use footprints provided in this repository!
