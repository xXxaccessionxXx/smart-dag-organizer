
import sys
import os
import traceback
import datetime
from PyQt6.QtWidgets import QMessageBox

class CrashHandler:
    @staticmethod
    def setup():
        """Installs the custom exception hook."""
        sys.excepthook = CrashHandler.handle_exception

    _save_callback = None

    @staticmethod
    def register_save_callback(callback):
        """Registers a function to be called on crash to save data."""
        CrashHandler._save_callback = callback

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Standard handler for uncaught exceptions."""
        # Attempt to save data first
        if CrashHandler._save_callback:
            try:
                print("Attempting emergency save...", file=sys.stderr)
                CrashHandler._save_callback()
                print("Emergency save completed.", file=sys.stderr)
            except Exception as e:
                print(f"Emergency save failed: {e}", file=sys.stderr)

        # Ignore KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # 1. Format the error
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_content = f"[{timestamp}] CRITICAL ERROR:\n{error_msg}\n{'-'*60}\n"

        # 2. Write to log file
        app_data = os.environ.get('APPDATA')
        if not app_data:
             app_data = os.path.expanduser("~")
        log_dir = os.path.join(app_data, "SmartDAGOrganizer")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "crash_log.txt")
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_content)
            log_path_msg = f"Details written to {os.path.abspath(log_file)}"
        except Exception as e:
            log_path_msg = f"Could not write to log: {e}"

        # 3. Print to console (for dev)
        print(log_content, file=sys.stderr)

        # 4. Show GUI Dialog
        # Try to find a parent, otherwise None
        from PyQt6.QtWidgets import QApplication
        parent = QApplication.activeWindow()
        
        error_box = QMessageBox(parent)
        error_box.setWindowTitle("Application Crash")
        error_box.setIcon(QMessageBox.Icon.Critical)
        
        # User Friendly Message
        error_box.setText("An unexpected error occurred!")
        error_box.setInformativeText(f"The application encountered a critical issue.\n\n{log_path_msg}\n\nError: {exc_value}")
        
        # Details button
        error_box.setDetailedText(error_msg)
        error_box.exec()
