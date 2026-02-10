
import os
import sys
import subprocess

def run_build():
    with open("build_debug.log", "w") as log:
        log.write("Starting isolated build...\n")
        
        icon_path = os.path.abspath("assets/icon.ico")
        log.write(f"Icon Path: {icon_path}\n")
        
        if not os.path.exists(icon_path):
            log.write("ERROR: Icon not found!\n")
            print("ERROR: Icon not found!")
            return

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src\\\\setup_wizard.py'],
    pathex=[],
    binaries=[],
    datas=[('payload.zip', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SmartDAG_Installer_Debug',
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
    icon={repr(icon_path)},
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SmartDAG_Installer_Debug',
)
"""
        with open("debug_setup.spec", "w") as f:
            f.write(spec_content)
        log.write("Created debug_setup.spec\n")
        
        cmd = [sys.executable, "-m", "PyInstaller", "debug_setup.spec", "--noconfirm", "--clean"]
        log.write(f"Running: {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            log.write("PyInstaller stdout:\n")
            log.write(result.stdout)
            log.write("\nPyInstaller stderr:\n")
            log.write(result.stderr)
            print("Build complete. check build_debug.log")
        except subprocess.CalledProcessError as e:
            log.write(f"PyInstaller Failed: {e}\n")
            log.write("Stdout:\n" + e.stdout)
            log.write("Stderr:\n" + e.stderr)
            print("Build FAILED.")

if __name__ == "__main__":
    run_build()
