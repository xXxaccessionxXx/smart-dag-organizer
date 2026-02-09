
import sys
import os
import traceback

# Redirect stdout/stderr to a file
log_file = open("crash_log.txt", "w")
sys.stdout = log_file
sys.stderr = log_file

print("Starting reproduction script...")

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("Failed to import PyQt6")
    sys.exit(1)

# Adjust path
sys.path.append(os.getcwd())

try:
    from src.config_manager import ConfigManager
    from src.settings_dialog import SettingsDialog
    print("Imports successful.")
except Exception as e:
    print(f"Import Error: {e}")
    traceback.print_exc()
    sys.exit(1)

def reproduction():
    print("Initializing QApplication...")
    app = QApplication(sys.argv)
    
    print("Initializing ConfigManager...")
    config = ConfigManager()
    
    class MockMainWindow:
        def apply_theme(self):
            print("Apply theme called")
            
    window = MockMainWindow()
    
    print("Attempting to create SettingsDialog...")
    try:
        dlg = SettingsDialog(config, parent=None, apply_callback=window.apply_theme)
        print("SettingsDialog created successfully!")
    except Exception as e:
        print(f"CRASHED during init: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        reproduction()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
    finally:
        print("Exiting.")
        log_file.close()
