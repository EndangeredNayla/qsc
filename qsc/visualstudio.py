import os
import subprocess
import sys

import qsc

if not qsc.is_windows():
    raise Exception("This is not Windows")

PROGRAM_FILES_X86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')

def _find_with_vswhere():
    try:
        proc = subprocess.run("vswherpe -products * -latest -prerelease -property installationPath", capture_output=True)
    except FileNotFoundError:
        return
    if proc.returncode != 0:
        sys.stderr.write(f"vswhere exited with return code {proc.returncode}: {proc.stder}")
        return
    return proc.stdout.strip()

def _find_vcvarsall():
    # try vswhere
    print("Trying vswhere")
    vswhere_base = _find_with_vswhere()
    if vswhere_base:
        vcvarsall = os.path.join(vswhere_base, b"VC\\Auxiliary\\Build\\vcvarsall.bat")
        if os.path.exists(vcvarsall):
            print(f"Found: {vcvarsall}")
            return vcvarsall

    # try standard installation locations
    for version in ('2019', '2017'):
        for edition in ('Enterprise', 'Professional', 'Community'):
            vcvarsall = f"{PROGRAM_FILES_X86}\\Microsoft Visual Studio\\{version}\\{edition}\\VC\\Auxiliary\\Build\\vcvarsall.bat"
            print(f"Trying standard location: {vcvarsall}")
            if os.path.exists(vcvarsall):
                print(f"Found: {vcvarsall}")
                return vcvarsall

    # special case for Visual Studio 2015 and earlier
    vcvarsall = f"{PROGRAM_FILES_X86}\\Microsoft Visual C++ Build Tools\\vcbuildtools.bat"
    if os.path.exists(vcvarsall):
        print(f"Found: {vcvarsall}")
        return vcvarsall

    raise Exception("Visual Studio not found")

def setup_visual_studio():
    # add standard location of vswhere to PATH, in case it's not there already
    os.environ['PATH'] += f'{os.pathsep}{PROGRAM_FILES_X86}\\Microsoft Visual Studio\\Installer'

    # find vcvarsall.bat
    vcvarsall = _find_vcvarsall()

    # run vcvarsall.bat
    args = "x64"
    proc = subprocess.run(f"set && cls && \"{vcvarsall}\" {args} && cls && set", shell="cmd", capture_output=True)
    if proc.returncode != 0:
        raise Exception(f"vcvarsall exited with code {proc.returncode}:\nstdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}")
    parts = proc.stdout.split(b"\f")
    old_env_output = parts[0]
    vcvars_output = parts[1]
    new_env_output = parts[2]

    # parse errors from vcvars, which if given bad arguments will error but still return successfully
    error_messages = [line for line in vcvars_output.split(b"\r\n") if line.startswith(b"[ERROR")]
    if error_messages:
        raise Exception(error_messages)

    # parse old environment variables
    old_env = {}
    for line in old_env_output.strip().split(b"\r\n"):
        key, value = line.split(b"=", 1)
        old_env[key] = value

    # parse new environment variables
    new_env = {}
    for line in new_env_output.strip().split(b"\r\n"):
        key, value = line.split(b"=", 1)
        old = old_env.get(key)
        if old != value:
            new_env[key] = value

    # export environment
    for key, value in new_env.items():
        os.environ[key.decode(sys.getdefaultencoding())] = value.decode(sys.getdefaultencoding())
