
import sys
import os
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt

sys.path.append(os.getcwd())

from src.config_manager import ConfigManager
from src.settings_dialog import SettingsDialog

# Mock application for Qt widgets
app = QApplication(sys.argv)

def run_test():
    print("Testing Expanded Settings...")

    # 1. Config Defaults
    print("Testing ConfigManager Defaults...")
    cfg = ConfigManager("test_config_expanded.json")
    
    # Ensure fresh start
    if os.path.exists("test_config_expanded.json"):
        os.remove("test_config_expanded.json")
        cfg = ConfigManager("test_config_expanded.json")

    theme = cfg.get_theme()
    print(f"Default Theme: {theme}")
    if theme != "Dark":
        print("FAIL: Default theme should be Dark")
        sys.exit(1)

    hover = cfg.get_hover_persistence()
    print(f"Default Hover Persistence: {hover}")
    if not hover:
        print("FAIL: Default hover persistence should be True")
        sys.exit(1)
        
    autosave = cfg.get_auto_save_interval()
    print(f"Default Auto-Save: {autosave}")
    if autosave != 300:
        print("FAIL: Default autosave should be 300")
        sys.exit(1)
    
    print("PASS: Defaults okay")

    # 2. Settings Dialog Logic
    print("Testing SettingsDialog...")
    dialog = SettingsDialog(cfg)
    
    # Simulate user changing settings programmatically
    # Mocking UI interaction
    try:
        dialog.create_appearance_tab() # Ensure tabs created
        dialog.create_behavior_tab()
        
        # Change Theme
        dialog.combo_theme.setCurrentIndex(1) # Light (Coming Soon)
        
        # Change Hover
        dialog.chk_hover.setChecked(False)
        
        # Change AutoSave
        dialog.spin_autosave.setValue(600)
        
        # Save
        # self.accept() in dialog closes it, so we mock accept to avoiding blocking? 
        # Actually save_settings calls accept(). We can catch it or just let it close if we were running exec().
        # Since we are not running exec(), we just call save_settings()
        
        # We need to mock QMessageBox or it will block or crash if no GUI
        # Monkey patch QMessageBox
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information = lambda p, t, m: print(f"MsgBox Info: {t} - {m}")
        QMessageBox.warning = lambda p, t, m: print(f"MsgBox Warning: {t} - {m}")
        dialog.accept = lambda: print("Dialog Accepted")
        
        dialog.save_settings()
        
        # Verify Persistence
        print(f"New Theme: {cfg.get_theme()}")
        if cfg.get_theme() != "Light": # "Light (Coming Soon)" -> "Light" logic
             print(f"FAIL: Theme not saved correctly. Got {cfg.get_theme()}")
             sys.exit(1)
             
        print(f"New Hover: {cfg.get_hover_persistence()}")
        if cfg.get_hover_persistence():
             print("FAIL: Hover persistence should be False")
             sys.exit(1)

        print(f"New Auto-Save: {cfg.get_auto_save_interval()}")
        if cfg.get_auto_save_interval() != 600:
             print("FAIL: Auto-save should be 600")
             sys.exit(1)
             
        print("PASS: Validated Settings Save Logic")
        
    except Exception as e:
        print(f"FAIL: Dialog Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Cleanup
    if os.path.exists("test_config_expanded.json"):
        os.remove("test_config_expanded.json")

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_test()
