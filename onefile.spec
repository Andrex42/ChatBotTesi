# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

import site
import os

import sys
sys.setrecursionlimit(5000)

block_cipher = None

assert len(site.getsitepackages()) > 0

package_path = site.getsitepackages()[0]
for p in site.getsitepackages():
    if "site-package" in p:
        package_path = p
        break

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=None,
    datas=[(os.path.join(package_path, "chromadb"), "./chromadb"),
        ("./export_data", "./export_data"),
        ("./resources", "./resources"),
        ("./.env", ".")],
    hiddenimports=collect_submodules('chromadb'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    with_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='myApp',
    debug=False,
    strip=False,
    upx=True,
    console=True
)
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='myApp',
# )
