import sys

from cx_Freeze import setup, Executable

def get_rev():
    return open('.git/' + (open('.git/HEAD').read().strip().split(': ')[1])).read()[:7]

build_exe_options = {
    "include_files": ["icon.ico"],
    "packages": ["PySide", "bitcoinrpc"],
    "optimize": 2,
    }

build_exe_options["constants"] = [
    "BUILD_REV='%s'" % get_rev()
    ]

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="ChainSign",
      version="0.1",
      description="ChainSign blockchain signing and timestamping app",
      executables=[
          Executable("chainsign.py", base=base, icon="icon.ico"),
          Executable("chainsign.py", base=None,
              targetName="chainsign_debug.exe", icon="icon.ico"),
          ],
      options={"build_exe": build_exe_options})
