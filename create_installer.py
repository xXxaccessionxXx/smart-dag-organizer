
import os
import shutil
import subprocess
import zipfile
import sys

def run_command(cmd):
    print(f"[Exec] {cmd}")
    subprocess.check_call(cmd, shell=True)

def create_installer():
    print("="*60)
    print("   Smart DAG Organizer - Installer Builder")
    print("="*60)

    # 1. Build Main Application
    print("\n[1/4] Building Main Application...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
        
    run_command("pyinstaller main.spec")

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
        f'pyinstaller --noconfirm --onefile --windowed --name "SmartDAG_Setup" '
        f'--add-data "{payload_zip};." '
        # f'--icon "assets/icon.bmp" ' # Icon disabled due to environment issues
        f'"src/setup_wizard.py"'
    )
    
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
                commit_msg = "Update: New Release"
                
            print("Pushing to GitHub...")
            run_command("git add .")
            run_command(f'git commit -m "{commit_msg}"')
            run_command("git push origin master") # Assuming master, could detect branch
            print("\n[Success] Pushed to GitHub!")
            
        except Exception as e:
            print(f"\n[Error] Release automation failed: {e}")

if __name__ == "__main__":
    create_installer()
