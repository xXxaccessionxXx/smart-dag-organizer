
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from themes import ThemeManager
# Mock Config to test logic without GUI
class MockConfig:
    def get_theme(self): return "Neon"
    def is_gradient_enabled(self): return True

print("Testing Main Theme Manager...")
neon = ThemeManager.get_theme("Neon")
if neon["button_fg"] == "#00f0ff": # Cyan
    print("PASS: Neon theme updated to Cyberpunk palette.")
else:
    print(f"FAIL: Neon theme color mismatch. Got {neon['button_fg']}")

print("Testing Gradient Generation...")
sheet = ThemeManager.get_stylesheet("Neon", use_gradient=True)
if "qlineargradient" in sheet and "stop:1 #221c35" in sheet: # Check for specific end color of new gradient
    print("PASS: Gradient stylesheet generated correctly with new colors.")
else:
    print("FAIL: Gradient stylesheet missing or incorrect.")

# Test Modules Integration (Import check mostly)
print("Testing Module Imports for Gradient Support...")
try:
    from src.workflow_organizer import WorkflowOrganizer
    from src.script_library import ScriptLibrary
    print("PASS: Modules imported successfully with new changes.")
except ImportError as e:
    print(f"FAIL: Import error handling modules: {e}")
except Exception as e:
    # Instantiation might fail without QApplication, which is fine
    print(f"WARN: runtime init might fail testing here: {e}")

print("Done.")
