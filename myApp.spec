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
    binaries=[],
    datas=[(os.path.join(package_path, "chromadb"), "./chromadb"),
        ("./export_data", "./export_data"),
        ("./resources", "./resources"),
        ("./.env", ".")],
    hiddenimports=collect_submodules('chromadb'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
a.datas += Tree('venv/Lib/site-packages/chromadb', prefix='chromadb')
a.datas += Tree('export_data', prefix='export_data')
a.datas += Tree('export_data', prefix='export_data')

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='myApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='myApp',
)
