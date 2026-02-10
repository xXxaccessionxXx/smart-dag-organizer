
import os
import shutil
import subprocess
import zipfile
import sys
import base64
import struct
import os

def generate_ico(filename):
    print(f"[Icon] Generating icon to {filename}...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    original_png = os.path.join(base_dir, "assets", "acyclic.PNG")
    
    # 1. Native PowerShell Conversion (Best Quality)
    # Tries to create a proper multi-size ICO or at least valid header via .NET
    ps_native_script = (
        f"$path = '{original_png}'; "
        f"$out = '{filename}'; "
        "Add-Type -AssemblyName System.Drawing; "
        "$img = [System.Drawing.Image]::FromFile($path); "
        "$bmp = new-object System.Drawing.Bitmap($img, 64, 64); " # 64x64 base
        "$hicon = $bmp.GetHicon(); "
        "$icon = [System.Drawing.Icon]::FromHandle($hicon); " 
        "$fs = New-Object System.IO.FileStream($out, [System.IO.FileMode]::Create); "
        "$icon.Save($fs); "
        "$fs.Close(); "
        "$icon.Dispose(); $bmp.Dispose(); $img.Dispose(); "
        "[Runtime.InteropServices.Marshal]::ReleaseComObject($hicon) | Out-Null;"
    )
    
    print("[Icon] Attempting native PowerShell conversion...")
    try:
        cmd = ["powershell", "-noprofile", "-command", ps_native_script]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[Icon] Native conversion failed: {e}")

    # Check validity (Native sometimes produces empty files in headless envs)
    native_success = False
    if os.path.exists(filename) and os.path.getsize(filename) > 1000: # >1KB means likely valid
        print("[Icon] Native conversion successful.")
        native_success = True
    else:
        print("[Icon] Native conversion produced invalid file (too small).")
    
    if not native_success:
        print("[Icon] Falling back to Manual PNG Wrapping (48x48)...")
        # 2. Manual PNG Wrapping (Robust Fallback)
        # Use 48x48 PNG - very standard size, less likely to trigger WinError 87 than 256
        target_size = 48
        resized_png = os.path.join(base_dir, "assets", f"icon_{target_size}.png")
        
        # Resize first
        if os.path.exists(original_png):
            ps_resize_script = (
                f"$path = '{original_png}'; "
                f"$out = '{resized_png}'; "
                "Add-Type -AssemblyName System.Drawing; "
                "$img = [System.Drawing.Image]::FromFile($path); "
                f"$new = new-object System.Drawing.Bitmap({target_size},{target_size}); "
                "$g = [System.Drawing.Graphics]::FromImage($new); "
                "$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic; "
                f"$g.DrawImage($img, 0, 0, {target_size}, {target_size}); "
                "$new.Save($out, [System.Drawing.Imaging.ImageFormat]::Png); "
                "$img.Dispose(); $new.Dispose(); $g.Dispose();"
            )
            try:
                subprocess.check_call(["powershell", "-noprofile", "-command", ps_resize_script], 
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except: pass
            
        source_png = resized_png if os.path.exists(resized_png) else original_png
        
        if os.path.exists(source_png):
            try:
                with open(source_png, "rb") as f:
                    png_data = f.read()
                
                # Check dimensions if possible or assume from target_size if resized
                # 48x48
                ico_header = struct.pack('<HHI', 0, 1, 1)
                
                # If using original (huge), these bytes might be wrong, but we tried resizing.
                # Assuming 48x48 for directory entry
                w_byte = 48
                h_byte = 48
                bpp = 32
                img_size = len(png_data)
                offset = 6 + 16
                
                dir_entry = struct.pack('<BBBBHHII', 
                    w_byte, h_byte, 0, 0, 1, bpp, img_size, offset
                )
                
                with open(filename, 'wb') as f:
                    f.write(ico_header)
                    f.write(dir_entry)
                    f.write(png_data)
                print(f"[Icon] Created manual ICO from {source_png}")
            except Exception as e:
                print(f"[Icon] Manual creation failed: {e}")

    # 3. Last Resort Fallback
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        print(f"[Icon] Using emergency fallback icon.")
        valid_ico_b64 = (
            "AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAA"
            "/4DAAN8BAAD/AAAA/wAAAO8AAAD3AAAA5wAAAOcAAAD3AAAA7wAAAP8AAAD/AAAA3wEAAP+AwAD/gMAA/4DAAP+AwAA="
        )
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(valid_ico_b64))


def run_command(cmd):
    print(f"[Exec] {cmd}")
    subprocess.check_call(cmd, shell=True)

def create_installer():
    print("="*60)
    print("   Smart DAG Organizer - Installer Builder")
    print("="*60)
    

    # Ensure Icon Exists (v2 to bypass locks)
    icon_file = "assets/icon_final.ico"
    generate_ico(icon_file)

    # 0. Sync with Remote
    print("\n[0/5] Syncing with Remote...")
    try:
        run_command("git pull origin master")
    except Exception as e:
        print(f"[Error] Git pull failed: {e}")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            sys.exit(1)

    # 1. Build Main Application
    print("\n[1/4] Building Main Application...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
        
    # Update main.spec if needed (simple sed-like replace in memory?)
    # Or just pass --icon to PyInstaller?
    # main.spec defines the icon. We should update main.spec or rely on PyInstaller overriding it?
    # PyInstaller's EXE step takes icon.
    # main.spec has `icon='assets\\icon.ico'` or similar.
    # checking main.spec content...
    
    # Let's just update main.spec dynamically
    spec_path = "main.spec"
    with open(spec_path, "r") as f:
        spec_content = f.read()
    
    if "icon='assets\\\\icon.ico'" in spec_content:
        spec_content = spec_content.replace("icon='assets\\\\icon.ico'", f"icon='{icon_file.replace('/', '\\\\')}'")
        with open(spec_path, "w") as f:
            f.write(spec_content)
            
    # Also check for single backslash
    if "icon='assets\\icon.ico'" in spec_content:
        spec_content = spec_content.replace("icon='assets\\icon.ico'", f"icon='{icon_file.replace('/', '\\\\')}'")
        with open(spec_path, "w") as f:
            f.write(spec_content)

    run_command(f'"{sys.executable}" -m PyInstaller main.spec')


    # 2. Create Payload Zip
    print("\n[2/4] Creating Payload Zip...")
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
    # main.spec should have added them, but let's be safe for user data templates
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

    # 3. Build Setup Executable
    print("\n[3/4] Building Setup Wizard...")
    
    # PyInstaller command for the installer
    # --onefile: Single exe
    # --windowed: No console
    # --add-data: Embed the zip
    # --icon: Icon for the setup exe
    
    setup_cmd = (
        f'"{sys.executable}" -m PyInstaller --noconfirm --onefile --windowed --name "SmartDAG_Setup" '
        f'--add-data "{payload_zip};." '
    )
    
    if os.path.exists("assets/icon_final.ico"):
        setup_cmd += f' --icon "assets/icon_final.ico" '
        
    setup_cmd += f'"src/setup_wizard.py"'
    
    # We might need to temporarily copy setup_wizard to root to avoid path issues with imports?
    # Actually, setup_wizard imports PyQt6, which is installed.
    # It doesn't import src modules? logic is self-contained.
    # checking setup_wizard.py... it uses standard libs and PyQt6 being installed.
    # It does NOT import src.* except... wait.
    
    run_command(setup_cmd)

    # 4. Cleanup
    print("\n[4/4] Cleaning up...")
    if os.path.exists(payload_zip):
        os.remove(payload_zip)
        
    # Move setup to root?
    setup_exe = "dist/SmartDAG_Setup.exe"
    if os.path.exists(setup_exe):
        shutil.move(setup_exe, "SmartDAG_Setup.exe")
        print(f"\n[Success] Installer created: SmartDAG_Setup.exe")
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
            # Check if version should be bumped
            import json
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
            
            # Git Commands
            commit_msg = input("Enter commit message (default: 'Update: New Release'): ").strip()
            if not commit_msg:
                commit_msg = f"Release {new_ver}"
                
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
            tag_name = f"v{new_ver}"
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
