# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for PDFIndsigt — Windows .exe (single file)."""

import os

block_cipher = None
root = os.path.dirname(os.path.abspath(SPECPATH))

a = Analysis(
    [os.path.join(root, 'main.py')],
    pathex=[root],
    binaries=[],
    datas=[
        (os.path.join(root, 'i18n'), 'i18n'),
        (os.path.join(root, 'assets'), 'assets'),
    ],
    hiddenimports=[
        'pikepdf',
        'pikepdf._core',
        'pypdf',
        'ttkbootstrap',
        'ttkbootstrap.themes',
        'ttkbootstrap.themes.standard',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDFIndsigt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(root, 'assets', 'icon.ico') if os.path.exists(os.path.join(root, 'assets', 'icon.ico')) else None,
)
