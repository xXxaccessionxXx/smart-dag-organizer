
import sys
import os
import shutil
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

sys.path.append(os.getcwd())
app = QApplication(sys.argv)

from src.config_manager import ConfigManager
from src.workflow_organizer import SmartWorkflowOrganizer

def run_test():
    print("Testing ConfigManager...")
    config = ConfigManager("test_config.json")
    
    # Reset config
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    
    # Test Default
    path = config.get_data_path()
    print(f"Default Path: {path}")
    if "genesis_data.json" not in path:
        print("FAIL: Default path incorrect")
        sys.exit(1)
        
    # Test Set
    new_path = os.path.abspath("test_data/my_data.json")
    config.set("data_path", new_path)
    
    # Reload
    config2 = ConfigManager("test_config.json")
    if config2.get_data_path() != new_path:
        print(f"FAIL: Logic did not persist path. Got {config2.get_data_path()}")
        sys.exit(1)
    print("PASS: Config persistence")
    
    print("Testing Workflow Organizer Integration...")
    # Inject test config
    win = SmartWorkflowOrganizer()
    win.config_manager = config # Override
    win.save_file_path = config.get_data_path()
    
    print(f"Window Data Path: {win.save_file_path}")
    if win.save_file_path != new_path:
        print("FAIL: Window did not pick up new path")
        sys.exit(1)
    
    print("PASS: Integration")

    # Cleanup
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    if os.path.exists("test_data"):
        try:
            shutil.rmtree("test_data")
        except:
            pass

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_test()
