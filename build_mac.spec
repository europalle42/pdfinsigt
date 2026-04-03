# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for PDFIndsigt — macOS .app bundle."""

import os
import sys

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
        'PIL._tkinter_finder',
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
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDFIndsigt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='PDFIndsigt',
)

app = BUNDLE(
    coll,
    name='PDFIndsigt.app',
    icon=os.path.join(root, 'assets', 'icon.icns') if os.path.exists(os.path.join(root, 'assets', 'icon.icns')) else None,
    bundle_identifier='dk.pdfinsigt.app',
    info_plist={
        'CFBundleName': 'PDFIndsigt',
        'CFBundleDisplayName': 'PDFIndsigt',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
)
