# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, copy_metadata

import os

onnx_asr_datas, onnx_asr_binaries, onnx_asr_hiddenimports = collect_all('onnx_asr')

datas = [('assets', 'assets')] + copy_metadata('onnx-asr') + onnx_asr_datas
if os.path.exists('models'):
    datas += [('models', 'models')]

binaries = onnx_asr_binaries
hiddenimports = ['onnx_asr'] + onnx_asr_hiddenimports

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tensorflow', 'matplotlib', 'scipy', 'pandas', 'PIL',
        'tkinter', 'IPython', 'notebook', 'anyio', 'pygments',
        'cv2', 'pytest', 'unittest', 'pydoc'
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PITCH',
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
    icon=['icon.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PITCH',
)
