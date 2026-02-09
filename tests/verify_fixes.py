
import sys
import os
import shutil
from PyQt6.QtWidgets import QApplication

# Ensure src in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Mock App
app = QApplication(sys.argv)

def test_crash_fix():
    print("\n--- Testing Crash Fix (apply_theme) ---")
    try:
        from src.workflow_organizer import SmartWorkflowOrganizer
        # Mock ConfigManager Singleton/Instance for test
        from config_manager import ConfigManager
        
        # We need to instantiate simple version without full GUI blocking
        # But SmartWorkflowOrganizer is a Main Window. 
        # We can just instantiate it and call apply_theme.
        
        window = SmartWorkflowOrganizer()
        
        print("Calling apply_theme()...")
        window.apply_theme()
        print("PASS: apply_theme() completed without AttributeError.")
        
    except AttributeError as e:
        print(f"FAIL: AttributeError: {e}")
    except Exception as e:
        print(f"FAIL: Unexpected Error: {e}")

def test_node_style():
    print("\n--- Testing Node Style ---")
    try:
        from src.workflow_organizer import SmartNode
        # Just check if paint method is present (basic sanity regex check done by agent previously)
        # We can check if 'QPainterPath' is in the source code of the paint method?
        # Or just instantiation.
        node = SmartNode("Test", 0, 0, None)
        print("PASS: SmartNode instantiated.")
    except Exception as e:
        print(f"FAIL: Node instantiation error: {e}")

if __name__ == "__main__":
    try:
        test_crash_fix()
        test_node_style()
    except Exception as e:
        print(f"CRITICAL TEST FAIL: {e}")
