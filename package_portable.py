
import os
import zipfile
import shutil
import sys

def create_portable_zip():
    print("Creating Portable Package...")
    
    # Paths
    dist_dir = "dist/SmartDAGOrganizer"
    output_zip = "SmartDAG_Portable.zip"
    
    # Check if build exists
    if not os.path.exists(dist_dir):
        print(f"[Error] Build directory '{dist_dir}' not found.")
        print("Please run 'builder.bat' or 'pyinstaller main.spec' first.")
        return

    # Create Zip
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Add Executable and Dependencies
            print(f"Archiving: {dist_dir}...")
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Relativize path so it sits at root of zip or inside specific folder?
                    # Usually portable apps sit in a folder. Let's keep the folder structure.
                    arcname = os.path.relpath(file_path, "dist") 
                    zipf.write(file_path, arcname)
            
            # 2. Add Default Config (Optional)
            if os.path.exists("config.json"):
                print("Adding: config.json")
                zipf.write("config.json", "SmartDAGOrganizer/config.json")
            
            # 3. Add Data Folder (Empty structure or default scripts)
            if os.path.exists("data"):
                print("Adding: data/ folder")
                for root, dirs, files in os.walk("data"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join("SmartDAGOrganizer", os.path.relpath(file_path, "."))
                        zipf.write(file_path, arcname)

            # 4. Add Readme/Walkthrough
            if os.path.exists("walkthrough.md"):
                print("Adding: walkthrough.md")
                zipf.write("walkthrough.md", "SmartDAGOrganizer/README.md")

        print(f"\n[Success] Portable package created: {os.path.abspath(output_zip)}")
        
    except Exception as e:
        print(f"\n[Error] Failed to create zip: {e}")

if __name__ == "__main__":
    create_portable_zip()
