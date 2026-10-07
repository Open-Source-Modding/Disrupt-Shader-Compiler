# WATCH_DOGS Shader Compiler

Recompiles the shader database for WATCH_DOGS 1 from the game's own HLSL sources.
The scripts drive `fxc.exe` over each shader family and write the compiled objects
with the header stub the engine loads.

The `.fx` sources belong to the game and are not in this repository. Unpack your own copy.

## Requirements

1. [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/) for `fxc.exe`
2. [Python](https://www.python.org/downloads/) 3

## Get the shader sources

1. Unpack `[WATCH_DOGS Install Directory]\data_win64\shaders.dat` with
   [Gibbed.Disrupt](https://github.com/Open-Source-Modding/Gibbed.Disrupt).
2. Copy the unpacked `engine` folder into this repository's root, next to `CompileShaders.py`.

The scripts read `engine\shaders\...` from the repository root. Shader family names
live in `engine\shaders\meta\filelist.meta.xml.txt`.

## Compile

1. Add the Windows SDK x64 directory to `PATH`, for example
   `F:\Windows Kits\10\bin\10.0.26100.0\x64\`.
2. Run `CompileShaders.py`.
3. Enter a shader family, for example `Mesh_DriverGeneric`. Enter `.fx` to build the
   whole database.

**Build the whole database once before you build a single family.** Families share
input and output signatures, so a family built on its own disagrees with the rest and
the game stops drawing.

Compiled objects land in `COMPILED`, and the script resumes where it stopped if you
run it again.

## Load the compiled shaders

1. Unpack `[WATCH_DOGS Install Directory]\data_win64\shadersobj.fat` with Gibbed.Disrupt.
2. Rename `shadersobj.fat` to `shadersobj.fat.bak`, and `shadersobj.dat` to `shadersobj.dat.bak`.
3. Move the unpacked `shadersobj_unpack\engine` folder into `[WATCH_DOGS Install Directory]\data_win64\`.

The engine then reads shader files from disk.

## Linux

`compile_shaders_linux.py` is the Linux port. It calls DXC instead of `fxc.exe`, keeps
paths in forward-slash form, and resolves the source filename case that the Windows
command list gets wrong. Install the DirectX Shader Compiler, then either put `dxc` on
`PATH` or set `DXC` to its full path and run:

```bash
python3 compile_shaders_linux.py Mesh_DriverGeneric
```

## License

Public domain. See `LICENSE`.
