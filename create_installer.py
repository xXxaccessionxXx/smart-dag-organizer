
import os
import shutil
import subprocess
import zipfile
import sys
import base64
import struct
import json

def generate_ico(filename):
    print(f"[Icon] Generating icon to {filename} using Pillow...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    original_png = os.path.join(base_dir, "assets", "acyclic.PNG")

    try:
        from PIL import Image
        if os.path.exists(original_png):
            img = Image.open(original_png)
            # Create high-quality multi-size ICO
            # Include 256x256, 128x128, 64x64, 48x48, 32x32, 16x16
            # This ensures crisp rendering at all scales and avoids "Single Image" issues.
            icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            img.save(filename, format='ICO', sizes=icon_sizes)
            print(f"[Icon] Successfully created multi-size ICO: {filename}")
            return
        else:
            print(f"[Icon] Source image not found: {original_png}")

    except ImportError:
        print("[Icon] Pillow (PIL) not installed. Please run: pip install Pillow")
        print("[Icon] Attempting fallback (PowerShell)...")
        # Native PowerShell Fallback (Single size 64x64)
        ps_native_script = (
            f"$path = '{original_png}'; "
            f"$out = '{filename}'; "
            "Add-Type -AssemblyName System.Drawing; "
            "$img = [System.Drawing.Image]::FromFile($path); "
            "$bmp = new-object System.Drawing.Bitmap($img, 64, 64); "
            "$hicon = $bmp.GetHicon(); "
            "$icon = [System.Drawing.Icon]::FromHandle($hicon); " 
            "$fs = New-Object System.IO.FileStream($out, [System.IO.FileMode]::Create); "
            "$icon.Save($fs); "
            "$fs.Close(); "
            "$icon.Dispose(); $bmp.Dispose(); $img.Dispose(); "
            "[Runtime.InteropServices.Marshal]::ReleaseComObject($hicon) | Out-Null;"
        )
        try:
             subprocess.check_call(["powershell", "-noprofile", "-command", ps_native_script], 
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
             if os.path.exists(filename) and os.path.getsize(filename) > 100:
                 print("[Icon] PowerShell fallback successful.")
                 return
        except: pass

    except Exception as e:
        print(f"[Icon] Generation failed: {e}")

    # Ultimate Fallback
    print(f"[Icon] Using emergency fallback standard icon.")
    valid_ico_b64 = (
        "AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAA"
        "/4DAAN8BAAD/AAAA/wAAAO8AAAD3AAAA5wAAAOcAAAD3AAAA7wAAAP8AAAD/AAAA3wEAAP+AwAD/gMAA/4DAAP+AwAA="
    )
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(valid_ico_b64))
    print(f"[Icon] Generated fallback {filename}")


def run_command(cmd):
    print(f"[Exec] {cmd}")
    subprocess.check_call(cmd, shell=True)

def update_version():
    """Prompts for version update and updates files."""
    print("\n[0/5] Version Check...")
    current_ver = "1.0.0"
    if os.path.exists("version.json"):
        with open("version.json", "r") as f:
            data = json.load(f)
            current_ver = data.get("version", "1.0.0")
    
    print(f"Current Version: {current_ver}")
    new_ver = input(f"Enter new version (or press Enter to keep {current_ver}): ").strip()
    
    if new_ver:
        # Update version.json
        if os.path.exists("version.json"):
            with open("version.json", "r") as f:
                data = json.load(f)
            data["version"] = new_ver
            with open("version.json", "w") as f:
                json.dump(data, f, indent=4)
            print(f"Updated version.json to {new_ver}")

        # Update src/version.py
        ver_py_path = "src/version.py"
        if os.path.exists(ver_py_path):
            with open(ver_py_path, "r") as f:
                lines = f.readlines()
            with open(ver_py_path, "w") as f:
                for line in lines:
                    if line.startswith("APP_VERSION ="):
                        f.write(f'APP_VERSION = "{new_ver}"\n')
                    else:
                        f.write(line)
            print(f"Updated src/version.py to {new_ver}")
        return new_ver
    return current_ver

def create_installer():
    print("="*60)
    print("   Smart DAG Organizer - Installer Builder")
    print("="*60)
    
    # 0. Version Update (BEFORE Build)
    version = update_version()

    # Ensure Icon Exists
    icon_file = "assets/icon.ico"
    generate_ico(icon_file)

    # 1. Sync with Remote (Optional, ask user?)
    # For now, let's just pull to ensure we are up to date, but be careful not to overwrite local changes if dirty?
    # User said "The current create_installer.py flow is good", so let's keep the pull.
    print("\n[1/5] Syncing with Remote...")
    try:
        run_command("git pull origin master")
    except Exception as e:
        print(f"[Error] Git pull failed: {e}")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            sys.exit(1)

    # 2. Build Main Application
    print("\n[2/5] Building Main Application...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
        
    # Safety Check: Ensure icon exists and matches spec expectation
    if not os.path.exists(icon_file):
        print(f"[Error] Generated icon {icon_file} not found! Build will fail.")
        sys.exit(1)
        
    # Update main.spec dynamically to ensure it matches
    spec_path = "main.spec"
    if os.path.exists(spec_path):
        with open(spec_path, "r") as f:
            spec_content = f.read()
        
        # Check for v2 or other legacy names and replace with correct one
        updated = False
        if "icon='assets\\\\icon_v2.ico'" in spec_content:
             print("[Info] Updating main.spec icon path (legacy v2 -> icon.ico)...")
             spec_content = spec_content.replace("icon='assets\\\\icon_v2.ico'", "icon='assets\\\\icon.ico'")
             updated = True
        elif "icon='assets\\icon_v2.ico'" in spec_content:
             print("[Info] Updating main.spec icon path (legacy v2 -> icon.ico)...")
             spec_content = spec_content.replace("icon='assets\\icon_v2.ico'", "icon='assets\\icon.ico'")
             updated = True
             
        if updated:
             with open(spec_path, "w") as f:
                 f.write(spec_content)

    run_command(f'"{sys.executable}" -m PyInstaller main.spec')


    # 3. Create Payload Zip
    print("\n[3/5] Creating Payload Zip...")
    payload_zip = "payload.zip"
    dist_dir = "dist/SmartDAGOrganizer"
    
    if os.path.exists(payload_zip):
        os.remove(payload_zip)
        
    with zipfile.ZipFile(payload_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
                
    # Add Data/Config if they exist in root but not in dist (depending on main.spec)
    if os.path.exists("data"):
        with zipfile.ZipFile(payload_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
             for root, dirs, files in os.walk("data"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join("data", os.path.relpath(file_path, "data"))
                    try:
                        zipf.getinfo(arcname)
                    except KeyError:
                        zipf.write(file_path, arcname)

    print(f"Payload created: {os.path.abspath(payload_zip)}")

    # 4. Build Setup Executable
    print("\n[4/5] Building Setup Wizard...")
    
    # Define icon path
    icon_abs = os.path.abspath("assets/icon.ico")
    
    # Manually generate setup.spec to ensure icon path is correct (string, not list)
    setup_spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

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
    a.binaries,
    a.datas,
    [],
    name='SmartDAG_Installer_Fixed',
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
    icon={repr(icon_abs) if os.path.exists(icon_abs) else 'None'},
)
"""
    with open("setup.spec", "w") as f:
        f.write(setup_spec_content)
        
    print(f"Generated setup.spec with icon: {icon_abs}")
    
    run_command(f'"{sys.executable}" -m PyInstaller setup.spec')

    # Cleanup
    if os.path.exists(payload_zip):
        os.remove(payload_zip)
        
    # Move setup to root?
    setup_exe = "dist/SmartDAG_Installer_Fixed.exe"
    if os.path.exists(setup_exe):
        shutil.move(setup_exe, "SmartDAG_Installer_Fixed.exe")
        print(f"\n[Success] Installer created: SmartDAG_Installer_Fixed.exe")
    else:
        print("\n[Error] Setup executable not found in dist/")

    # 5. Git & Release Automation
    if "--build-only" in sys.argv:
        print("\n[Info] Build Only mode: Skipping release automation.")
        return

    print("\n[5/5] Release Automation")
    do_release = input("Do you want to push this release to GitHub? (y/N): ").strip().lower()
    
    if do_release == 'y':
        try:
            # Git Commands
            commit_msg = input("Enter commit message (default: 'Update: New Release'): ").strip()
            if not commit_msg:
                commit_msg = f"Release {version}"
                
            print("Pushing to GitHub...")
            run_command("git add .")
            run_command(f'git commit -m "{commit_msg}"')
            
            # Robust Push Logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"Push attempt {attempt+1}/{max_retries}...")
                    run_command("git push origin master")
                    break # Success!
                except subprocess.CalledProcessError:
                    print("\n[Warning] Push failed. Remote might have new changes.")
                    if attempt < max_retries - 1:
                        print("Attempting to pull and rebase...")
                        try:
                            run_command("git pull --rebase origin master")
                        except Exception as e:
                             print(f"[Error] Rebase failed: {e}. Please resolve conflicts manually.")
                             sys.exit(1)
                    else:
                        print("\n[Error] Failed to push after multiple attempts.")
                        sys.exit(1)
            
            # Push Tag to trigger GitHub Action
            tag_name = f"v{version}"
            print(f"Pushing tag {tag_name} to trigger release build...")
            
            # Use -f to overwrite if it exists locally, and force push to remote
            run_command(f"git tag -f {tag_name}")
            run_command(f"git push origin {tag_name} --force")
            
            print("\n[Success] Pushed code and tag to GitHub!")
            print("[Info] GitHub Action will now build the release and upload artifacts.")
            
        except Exception as e:
            print(f"\n[Error] Release automation failed: {e}")

if __name__ == "__main__":
    create_installer()
