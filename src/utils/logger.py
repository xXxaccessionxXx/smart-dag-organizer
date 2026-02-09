
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

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Standard handler for uncaught exceptions."""
        # Ignore KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # 1. Format the error
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_content = f"[{timestamp}] CRITICAL ERROR:\n{error_msg}\n{'-'*60}\n"

        # 2. Write to log file
        log_file = "crash_log.txt"
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
