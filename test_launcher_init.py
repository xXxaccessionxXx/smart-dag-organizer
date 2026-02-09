
import sys
import os

print("Testing Launcher Instantiation...")
try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    pass

# Mocking ConfigManager behavior slightly if needed, but test should run real code
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# Ensure CWD is set correctly for imports inside modules that might check CWD
os.chdir(current_dir)

try:
    # Need an app instance for QMainWindow
    app = QApplication(sys.argv)
    
    from src.launcher import GenesisLauncher
    
    # Try to instantiate
    print("Initializing GenesisLauncher...")
    window = GenesisLauncher()
    print("PASS: GenesisLauncher instantiated without crash.")
    
    # Optional: Check if theme was applied (simple check)
    style = window.styleSheet()
    if "background-color" in style:
        print("PASS: Stylesheet applied.")
    else:
        print("WARN: Stylesheet might be empty?")
        
except Exception as e:
    print(f"FAIL: Crash during launcher init: {e}")
    # Print traceback
    import traceback
    traceback.print_exc()

print("Done.")
