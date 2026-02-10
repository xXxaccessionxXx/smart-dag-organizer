import sys
import os

# Add 'src' to the python path so imports find the modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from src.launcher import GenesisLauncher
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    try:
        # --- Crash Handler ---
        # We wrap the entire startup in a try-except block to catch import errors or early crashes
        # and display them in a native message box since we might not have a console.
        
        # 1. Console Toggle Logic
        # We check if the user wants the console effectively visible.
        # Since we plan to build with console=False (windowed), we need to AllocConsole if debug is ON.
        # We can check a command line arg or the config file.
        
        show_console = False
        if "--debug" in sys.argv:
            show_console = True
        else:
            # Try to read config without full ConfigManager overhead if possible?
            # Or just let ConfigManager handle it.
            # Let's use a simple check first to minimal dependencies.
            config_path = os.path.join(current_dir, "config.json")
            if os.path.exists(config_path):
                import json
                try:
                    with open(config_path, "r") as f:
                        data = json.load(f)
                        if data.get("show_console", False):
                            show_console = True
                except:
                    pass

        if show_console:
            import ctypes
            # Attach to existing console or allocate new one
            # If launched from cmd, attach? If double clicked, allocate.
            # AllocConsole fails if already has one, which is fine.
            ctypes.windll.kernel32.AllocConsole()
            # Redirect stdout/stderr (needed for python to write to it)
            sys.stdout = open('CONOUT$', 'w')
            sys.stderr = open('CONOUT$', 'w')
            print("Debug Console Active")

        # 2. Setup Crash Handler for later runtime errors
        from src.utils.logger import CrashHandler
        CrashHandler.setup()
        
        # 3. Launch App
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # Register app.save_data as a crash callback to ensure data is saved on unexpected exits
        CrashHandler.add_callback(app.save_data)

        # Ensure launcher applies theme globally
        window = GenesisLauncher()
        window.show()
        sys.exit(app.exec())
        
    except Exception as e:
        import traceback
        error_msg = f"Critical Startup Error:\n{str(e)}\n\n{traceback.format_exc()}"
        
        # Try to show MessageBox
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, error_msg, "Startup Failed", 0x10)
        except:
            # Last resort
            print(error_msg)
            with open("crash_startup.txt", "w") as f:
                f.write(error_msg)
        sys.exit(1)
