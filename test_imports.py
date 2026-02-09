
import sys
import os

print("Testing Imports...")
try:
    from PyQt6.QtWidgets import QApplication
    # app = QApplication([]) # Don't create app, just check imports
except ImportError:
    print("FAIL: PyQt6 not installed?")
    sys.exit(1)

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

try:
    import src.workflow_organizer
    print("PASS: workflow_organizer imported successfully")
except ImportError as e:
    print(f"FAIL: workflow_organizer import error: {e}")
except Exception as e:
    print(f"FAIL: workflow_organizer generic error: {e}")

try:
    import src.launcher
    print("PASS: launcher imported successfully")
except ImportError as e:
    print(f"FAIL: launcher import error: {e}")

print("Done.")
