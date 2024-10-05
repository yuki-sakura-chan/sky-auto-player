# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[('sakura','sakura')],
    hiddenimports=['pygame', 'pydirectinput', 'pynput', 'requests'],
    hookspath=['./hooks'],
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
    [],
    exclude_binaries=True,
    name='gui',
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
    icon='resources/static/icon/logo-64x64.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gui',
)

import os
import shutil

print('Copying resources...')
if not os.path.exists('dist/gui'):
    os.makedirs('dist/gui')
shutil.copyfile('config.yaml', 'dist/gui/config.yaml')
shutil.copytree('resources/', 'dist/gui/resources/')
