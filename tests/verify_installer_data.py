import os
import shutil
import tempfile
import json

def verify_installer_logic():
    # 1. Setup Mock Environment
    base_tmp = tempfile.mkdtemp()
    install_dir = os.path.join(base_tmp, "SmartDAGOrganizer")
    os.makedirs(install_dir)
    
    # Create dummy user data
    data_dir = os.path.join(install_dir, "data")
    os.makedirs(data_dir)
    with open(os.path.join(data_dir, "user_pipelines.json"), "w") as f:
        f.write('{"pipelines": ["My Project"]}')
        
    config_path = os.path.join(install_dir, "config.json")
    with open(config_path, "w") as f:
        f.write('{"theme": "Light"}')
        
    print(f"Created mock install at: {install_dir}")
    print("Populated with dummy user data.")
    
    # --- LOGIC UNDER TEST (Adapted from setup_wizard.py) ---
    print("\n--- Running Installer Logic ---")
    
    # Status: Checking for existing data...
    # --- DATA PRESERVATION START ---
    backup_dir = os.path.join(tempfile.gettempdir(), "SmartDAG_Backup_Test")
    has_backup = False
    
    INSTALL_DIR = install_dir # Alias for logic copy-paste compatibility
    
    if os.path.exists(INSTALL_DIR):
        try:
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            os.makedirs(backup_dir)
            
            # Backup 'data' folder
            data_src = os.path.join(INSTALL_DIR, "data")
            if os.path.exists(data_src):
                shutil.copytree(data_src, os.path.join(backup_dir, "data"))
                has_backup = True
                print("Backed up data folder.")
                
            # Backup 'config.json'
            config_src = os.path.join(INSTALL_DIR, "config.json")
            if os.path.exists(config_src):
                shutil.copy2(config_src, backup_dir)
                has_backup = True
                print("Backed up config.json.")
                
        except Exception as e:
            print(f"Backup warning: {e}")
    # --- DATA PRESERVATION END ---

    print("Cleaning up old files (Wiping Install Dir)...")
    if os.path.exists(INSTALL_DIR):
        shutil.rmtree(INSTALL_DIR)
    
    os.makedirs(INSTALL_DIR, exist_ok=True)

    print("Extracting files (Simulated)...")
    # Simulate extraction of default templates (which would overwrite if not handled)
    os.makedirs(os.path.join(INSTALL_DIR, "data"))
    with open(os.path.join(INSTALL_DIR, "data", "genesis_data.json"), "w") as f:
        f.write("{}") # Default empty
    # No config.json created by default usually, but let's say it updates
    
    # --- DATA RESTORE START ---
    if has_backup:
        print("Restoring user data...")
        try:
            # Restore 'data' folder (Overwrite templates)
            backup_data = os.path.join(backup_dir, "data")
            if os.path.exists(backup_data):
                target_data = os.path.join(INSTALL_DIR, "data")
                # shutil.copytree with dirs_exist_ok=True (Python 3.8+)
                shutil.copytree(backup_data, target_data, dirs_exist_ok=True)
                
            # Restore 'config.json'
            backup_config = os.path.join(backup_dir, "config.json")
            if os.path.exists(backup_config):
                shutil.copy2(backup_config, os.path.join(INSTALL_DIR, "config.json"))
                
            # Cleanup backup
            shutil.rmtree(backup_dir)
        except Exception as e:
             print(f"Data Restore Failed: {e}")
    # --- DATA RESTORE END ---
    
    print("--- Installer Logic Finished ---\n")
    
    # 3. Verification
    print("Verifying Data Preservation...")
    
    # Check User Data inside 'data'
    user_pipeline_file = os.path.join(install_dir, "data", "user_pipelines.json")
    if os.path.exists(user_pipeline_file):
        print("[Pass] 'data/user_pipelines.json' preserved.")
    else:
        print("[FAIL] 'data/user_pipelines.json' MISSING!")
        
    # Check Config
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            content = f.read()
        if 'Light' in content:
             print("[Pass] 'config.json' preserved (Theme: Light).")
        else:
             print(f"[FAIL] 'config.json' content mismatch: {content}")
    else:
        print("[FAIL] 'config.json' MISSING!")

    # Cleanup Test Envs
    shutil.rmtree(base_tmp)

if __name__ == "__main__":
    verify_installer_logic()
