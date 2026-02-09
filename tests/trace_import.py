
import sys
import os
import traceback

sys.path.append(os.getcwd())

with open("trace.txt", "w") as f:
    try:
        f.write("Starting import...\n")
        from src.settings_dialog import SettingsDialog
        f.write("Import success!\n")
    except Exception:
        f.write("Import FAILED:\n")
        f.write(traceback.format_exc())
