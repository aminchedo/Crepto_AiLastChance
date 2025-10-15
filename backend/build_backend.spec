# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for packaging FastAPI backend as standalone executable
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all hidden imports
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'pydantic',
    'sqlalchemy',
    'alembic',
    'redis',
    'tensorflow',
    'keras',
    'numpy',
    'pandas',
    'scikit-learn',
    'ta',
    'ccxt',
    'aiohttp',
    'websockets',
    'structlog',
    'prometheus_client',
    'passlib',
    'python_jose',
    'cryptography',
]

# Collect submodules
hiddenimports += collect_submodules('uvicorn')
hiddenimports += collect_submodules('fastapi')
hiddenimports += collect_submodules('pydantic')
hiddenimports += collect_submodules('sqlalchemy')
hiddenimports += collect_submodules('tensorflow')
hiddenimports += collect_submodules('keras')

# Collect data files
datas = []
datas += collect_data_files('tensorflow')
datas += collect_data_files('keras')
datas += collect_data_files('alembic')

# Add model files
datas += [('models', 'models')]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'PIL',
        'IPython',
        'jupyter',
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
    [],
    exclude_binaries=True,
    name='main',
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
    icon='../build/icon.ico' if sys.platform == 'win32' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)

