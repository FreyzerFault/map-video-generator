# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Para usar un .py externo hay que añadir el directorio de este archivo (SPEC) al path
sys.path.insert(0, os.path.dirname(SPEC))

import setup_bundle

version = '1.1.0'
program_name = 'Map Video Generator'

a = Analysis(
    ['src\\main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('README.md', '.')],
    hiddenimports=['utils.image_utils'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=f"{program_name} {version}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['video_map_gen_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Map Video Generator',
)


setup_bundle.setup_bundle_folder(program_name, version)