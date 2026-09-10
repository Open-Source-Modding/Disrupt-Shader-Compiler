#!/usr/bin/env python3
"""Linux build of Disrupt-Shader-Compiler pipeline.
Replaces fxc.exe with DXC (DirectX Shader Compiler), uses forward-slash paths.
Usage: python3 compile_shaders_linux.py [family]
If [family] omitted, prompts interactively."""
import os
import sys
import subprocess
import time
import shutil
import shlex
import concurrent.futures

# Microsoft DXC (cross-platform HLSL -> DXBC). Set DXC to an explicit path, or put dxc on PATH.
DXC = os.environ.get("DXC") or shutil.which("dxc") or "dxc"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COMMAND_FILE = os.path.join(SCRIPT_DIR, "Shader_Compile_Command_Sorted.txt")
SOURCE_DIR = SCRIPT_DIR + "/"          # forward slashes
COMPILE_DIR = os.path.join(SCRIPT_DIR, "COMPILED/")
STATE_FILE = os.path.join(SCRIPT_DIR, "compile_shaders_linux.txt")
NOMAD_PLATFORM = os.environ.get("NOMAD_PLATFORM", "LINUX")  # game runs under Wine-on-Linux, so DXBC target is Windows ABI

def get_shader_compile_arg(cmd: str) -> str:
    fo_pos = cmd.find("/Fo")
    return cmd[4:fo_pos - 1].replace("\\", "/")

def get_shader_source(cmd: str) -> str:
    start = cmd.find('" ".') + 5
    return cmd[start:len(cmd) - 1].replace("\\", "/")

def get_shader_dest(cmd: str) -> str:
    start = cmd.find('/Fo "') + 7
    end = cmd.find('" ".')
    return cmd[start:end].replace("\\", "/")

# Linux FS is case-sensitive, but Shader_Compile_Command_Sorted.txt was generated on
# Windows and references title-case paths (e.g. meta\\DeferredLighting.fx) while the
# on-disk files are lowercase (meta/deferredlighting.fx).  Build a lowercase->real
# path map once so dxc can actually find each source file.
_shader_root = os.path.join(SCRIPT_DIR, "engine", "shaders")
_LOWER_TO_REAL = {}
for _dir, _subs, _files in os.walk(_shader_root):
    for _f in _files:
        _full = os.path.join(_dir, _f)
        _rel = os.path.relpath(_full, _shader_root).replace("\\", "/")
        _LOWER_TO_REAL.setdefault(_rel.lower(), _rel)

def resolve_source_case(src_rel: str) -> str:
    """Resolve a (possibly wrong-case) source path to the real on-disk path.
    src_rel is 'engine/shaders/<...>' (full path from SCRIPT_DIR, forward slashes).
    The map is keyed on paths relative to engine/shaders/, so strip the prefix.
    Falls back to the given path unchanged if not found, so a real missing file
    still surfaces a clean 'no such file' from dxc."""
    rel = src_rel.replace("\\", "/")
    if rel.lower().startswith("engine/shaders/"):
        inner = rel[len("engine/shaders/"):]
        resolved = _LOWER_TO_REAL.get(inner.lower())
        if resolved:
            return "engine/shaders/" + resolved
    return src_rel

with open(COMMAND_FILE, "r", encoding="utf-8") as f:
    command_lines = f.read().splitlines()

last_family = ""
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        last_family = f.read().strip()

user_input = "" if len(sys.argv) > 1 else input(f"Shader family [{last_family}]: ").strip()
shader_family = user_input or (sys.argv[1] if len(sys.argv) > 1 else "") or last_family

with open(STATE_FILE, "w", encoding="utf-8") as f:
    f.write(shader_family + "\n")

jobs = []
seen = set()
for line in command_lines:
    if shader_family.lower() in line.lower() and line not in seen:
        seen.add(line)
        target = COMPILE_DIR + get_shader_dest(line)
        src_rel = get_shader_source(line)
        source = SOURCE_DIR + resolve_source_case(src_rel)
        compile_arg = (get_shader_compile_arg(line)
                       + f' /D NOMAD_PLATFORM_{NOMAD_PLATFORM} /Fo "{target}" "{source}"')
        jobs.append({"target": target, "source": source, "compile_arg": compile_arg})

print(f"Found {len(jobs)} compile jobs for '{shader_family}'")
engine_dir = os.path.join(COMPILE_DIR, "engine")
shutil.rmtree(engine_dir, ignore_errors=True)

def compile_shader(job):
    out_dir = os.path.dirname(job["target"])
    os.makedirs(out_dir, exist_ok=True)
    try:
        r = subprocess.run([DXC] + shlex.split(job["compile_arg"]), shell=False,
                            capture_output=True, text=True, timeout=60)
        return r.returncode, r.stderr[-500:] if r.returncode != 0 else ""
    except Exception as e:
        return -1, str(e)

mw = min(32, (os.cpu_count() or 4) * 2)
print(f"Compiling {len(jobs)} shaders with {mw} workers...")
with concurrent.futures.ThreadPoolExecutor(max_workers=mw) as executor:
    fut = {executor.submit(compile_shader, j): j for j in jobs}
    ok = fail = done = 0
    for f in concurrent.futures.as_completed(fut):
        rc, err = f.result()
        done += 1
        if rc == 0: ok += 1
        else:
            fail += 1
            if err and fail <= 5:
                print(f"FAIL: {fut[f]['source']}: {err.strip()[-200:]}")
        if done % 50 == 0:
            print(f"[{done}/{len(jobs)}] ok={ok} fail={fail}")

print(f"\nCompiled: {ok}/{len(jobs)} ok, {fail} failed")
