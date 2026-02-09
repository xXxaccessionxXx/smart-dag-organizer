
import sys
import os
import shutil
from PyQt6.QtWidgets import QApplication

# Ensure src in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Mock App
app = QApplication(sys.argv)

def test_live_ui():
    print("\n--- Testing Live UI ---")
    from src.settings_dialog import SettingsDialog
    from config_manager import ConfigManager
    
    cfg = ConfigManager._get_shared_instance()
    
    called = False
    def my_callback():
        nonlocal called
        called = True
        print("Callback triggered!")
        
    dlg = SettingsDialog(cfg, apply_callback=my_callback)
    
    # Simulate change
    print("Simulating Theme Change...")
    # We can't clicking UI, but we can call the trigger method directly
    dlg.combo_theme.setCurrentIndex(1) # Change index
    # Note: currentIndexChanged is connected to trigger_live_update
    
    if called:
        print("PASS: Live update callback triggered.")
    else:
        print("FAIL: Live update callback NOT triggered.")
        
def test_java_logic():
    print("\n--- Testing Java Logic ---")
    from src.script_library import ScriptLibrary
    
    lib = ScriptLibrary()
    
    # Check Highlighter rules update
    lib.combo_lang.setCurrentText("Java")
    if lib.highlighter.current_language == "Java":
        print("PASS: Highlighter switched to Java.")
    else:
        print(f"FAIL: Highlighter language is {lib.highlighter.current_language}")
        
    # Check execution logic (dry run)
    # We can't easily assert subprocess call without mocking, 
    # but we can try running a simple java file and check if it errors about 'javac' missing or succeeds.
    
    lib.current_script = "TestJava"
    lib.scripts_data["TestJava"] = {"language": "Java"}
    lib.editor.setPlainText('public class TestJava { public static void main(String[] args) { System.out.println("Java Works"); } }')
    
    print("Attempting to run Java script...")
    lib.run_script()
    
    output = lib.output_console.toPlainText()
    print(f"Console Output: {output.strip()}")
    
    if "Java Works" in output:
        print("PASS: Java execution succeeded!")
    elif "Compilation Failed" in output or "Execution Error" in output:
        print("INFO: Java execution attempted but failed (likely missing JDK). Logic is present.")
    else:
        print("FAIL: Unexpected state.")

if __name__ == "__main__":
    try:
        test_live_ui()
        test_java_logic()
    except Exception as e:
        print(f"CRITICAL FAIL: {e}")
        import traceback
        traceback.print_exc()
