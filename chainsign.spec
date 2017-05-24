# -*- mode: python -*-

block_cipher = None

def get_rev():
    return open('.git/' + (open('.git/HEAD').read().strip().split(': ')[1])).read()[:7]

with open('build/build_id.txt', 'w') as fd:
    fd.write(get_rev())

a = Analysis(['chainsign.py'],
             pathex=['.'],
             binaries=[],
             datas=[('build/build_id.txt', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='chainsign',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='assets/icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='chainsign')
