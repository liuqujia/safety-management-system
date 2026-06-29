# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# 解决 Windows 路径中文问题
sys.stdout.reconfigure(encoding='utf-8')

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        'requests',
        'urllib3',
        'charset_normalizer',
        'idna',
        'certifi',
        'openpyxl',
        'et_xmlfile',
        'PIL',
        'PIL.Image',
        'PIL._imaging',
        'dateutil',
        'dateutil.parser',
        'dateutil.relativedelta',
        'dateutil.rrule',
        'python_dotenv',
        'json',
        'io',
        'datetime',
        'locale',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='安全整改管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    # 解决 Windows 编码问题
    encoding_args=True,
)
