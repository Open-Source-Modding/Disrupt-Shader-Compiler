# WATCH_DOGS 1 Shader Compiler
This repo contains the tooling to recompile the shader database for WATCH_DOGS 1 from your own copy of the game.

## Requirements:
1. [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/)
2. [Python](https://www.python.org/downloads/)

## Getting the shader sources

The shader sources are the game's own files and are not shipped here. Unpack them from
your copy of the game first:

1. Unpack `Watch_Dogs\data_win64\shadersobj.fat` with [Gibbed.Disrupt](https://github.com/gibbed/Gibbed.Disrupt)
2. Copy the unpacked `engine` folder into this repo's root, next to `CompileShaders.py`

The scripts expect `engine\shaders\...` under the repo root, and family names come from
`engine\shaders\meta\filelist.meta.xml.txt` in that unpacked folder.

## Compilation
WARNING: You must recompile all shaders once before compiling a specific shader family to ensure consistent input/output signatures
- Clone the entire repo and place the unpacked `engine` folder in its root
- Add Windows SDK x64 path to your `PATH` environment variable (e.g. `F:\Windows Kits\10\bin\10.0.26100.0\x64\`)
- Run `CompileShaders.py`
- Enter a shader family you wish to compile (e.g. `Mesh_DriverGeneric`, family names can be found in `engine\shaders\meta\filelist.meta.xml.txt`)
- Or if you need to compile all shaders, type in `.fx` should compile everything

## Loading shaders from disk
- You can unpack `Watch_Dogs\data_win64\shadersobj.fat` with gibbed.disrupt, rename both `shadersobj.fat` and `shadersobj.dat` to `shadersobj.fat.bak` and `shadersobj.dat.bak`
- Move `Watch_Dogs\data_win64\shadersobj_unpack\engine` folder to `Watch_Dogs\data_win64\`
- Game will load from disk shader files from now on

