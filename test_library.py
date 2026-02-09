
import sys
import os
import shutil

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# Mock QApplication for non-GUI logic tests where possible
try:
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
except:
    pass

from src.script_library import ScriptLibrary

print("Testing Script Library Instantiation...")
try:
    lib = ScriptLibrary()
    print("PASS: ScriptLibrary instantiated.")
except Exception as e:
    print(f"FAIL: ScriptLibrary init failed: {e}")
    sys.exit(1)

print("Testing Search Logic...")
# Inject dummy data
lib.scripts_data = {
    "my_script": {"content": "print('hello')", "language": "Python"},
    "test_abc": {"content": "...", "language": "Plain Text"},
    "auto_generated": {"content": "...", "language": "Python"}
}
lib.refresh_lists()

# Test 1: Empty Search
lib.txt_search.setText("")
lib.refresh_lists()
count_user = lib.list_user.count()
count_auto = lib.list_auto.count()
if count_user == 2 and count_auto == 1:
    print("PASS: Empty search shows all.")
else:
    print(f"FAIL: Empty search count mismatch. User: {count_user}, Auto: {count_auto}")

# Test 2: Search 'test'
lib.txt_search.setText("test")
lib.refresh_lists()
if lib.list_user.count() == 1 and lib.list_user.item(0).text() == "test_abc":
    print("PASS: Search 'test' correct.")
else:
    print(f"FAIL: Search 'test' failed.")

# Test 3: Search 'auto'
lib.txt_search.setText("auto")
lib.refresh_lists()
if lib.list_auto.count() == 1 and lib.list_auto.item(0).text() == "auto_generated":
    print("PASS: Search 'auto' correct.")
else:
    print(f"FAIL: Search 'auto' failed.")
    
print("Done.")
