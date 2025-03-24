# ملف إعداد PyInstaller لإنشاء EXE
# تضمين جميع مكتبات streamlit تلقائيًا
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import PyInstaller.__main__

hidden_imports = collect_submodules("streamlit")
datas = collect_data_files("streamlit")

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="app",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
