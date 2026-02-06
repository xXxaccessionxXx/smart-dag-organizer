import sys
import os
import ctypes

# --- Safe Import Logic ---
def show_error_and_exit(missing_module):
    """Displays a native error dialog and exits."""
    message = (f"Error: Could not import '{missing_module}'.\n\n"
               "Please ensure you are running this script within the Python Virtual Environment.\n"
               "Try running: .venv\\Scripts\\python.exe launcher.py")
    title = "Dependency Missing"
    # 0x10 = MB_ICONHAND (Critical Error), 0x0 = MB_OK
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10 | 0x0)
    sys.exit(1)

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                                 QWidget, QLabel, QPushButton, QMessageBox)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QColor
except ImportError:
    show_error_and_exit("PyQt6")

# --- Import your existing tool ---
# This requires your previous script to be named 'workflow_organizer.py'
# Ensure current directory is in path (fixes issues when running from other directories)
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

try:
    from workflow_organizer import SmartWorkflowOrganizer
    from script_library import ScriptLibrary
    from src.ai.assistant import NeuralAssistant
    from config_manager import ConfigManager
except ImportError as e:
    SmartWorkflowOrganizer = None
    ScriptLibrary = None
    NeuralAssistant = None
    ConfigManager = None
    print(f"Import Error: {e}")

class GenesisLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Genesis - Hub")
        self.resize(800, 600)

        # Apply the consistent Dark Theme
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #d4d4d4; font-family: 'Segoe UI'; }
            QPushButton { 
                background-color: #252526; 
                color: white; 
                font-family: 'Segoe UI';
                font-size: 16px;
                border: 1px solid #3e3e42; 
                padding: 15px 30px; 
                border-radius: 8px;
                text-align: left;
            }
            QPushButton:hover { 
                background-color: #007acc; 
                border: 1px solid #007acc;
            }
            QPushButton:disabled {
                background-color: #1e1e1e;
                color: #555555;
                border: 1px dashed #3e3e42;
            }
        """)

        # Central Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(100, 60, 100, 60) # Generous margins for a clean look

        # --- Header Section ---
        title = QLabel("PROJECT GENESIS")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: white; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Select a module to begin")
        subtitle.setStyleSheet("font-size: 16px; color: #888888; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # --- Buttons Section ---
        # 1. The Workflow Organizer (Active)
        btn_workflow = QPushButton("📂   Workflow Organizer")
        btn_workflow.clicked.connect(self.launch_workflow)
        layout.addWidget(btn_workflow)

        # 2. Neural Assistant
        btn_ai = QPushButton("🤖   Neural Assistant")
        btn_ai.clicked.connect(self.launch_assistant)
        layout.addWidget(btn_ai)

        # 3. Script Library
        btn_scripts = QPushButton("📜   Script Library")
        btn_scripts.clicked.connect(self.launch_library) # Connect function
        btn_scripts.clicked.connect(self.launch_library) # Connect function
        layout.addWidget(btn_scripts)

        # 4. Settings / Toggle
        self.btn_toggle = QPushButton("Enable AI Module")
        self.btn_toggle.clicked.connect(self.toggle_ai)
        self.btn_toggle.setStyleSheet("background-color: #333333; font-size: 14px; padding: 10px;")
        layout.addWidget(self.btn_toggle)
        
        # Initial State
        self.btn_ai = btn_ai
        self.update_ui_state()

        layout.addStretch()

        # Footer
        footer = QLabel("System v1.1 | Ready")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #444444; font-size: 12px;")
        layout.addWidget(footer)

    def launch_workflow(self):
        if SmartWorkflowOrganizer:
            # Create the tool window
            self.tool_window = SmartWorkflowOrganizer()
            self.tool_window.show()
            # Close the menu (or use self.hide() if you want to keep it running)
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Could not find 'workflow_organizer.py'.\nMake sure both files are in the same folder.")

    def launch_library(self):
        if ScriptLibrary:
            self.lib_window = ScriptLibrary()
            self.lib_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Could not find 'script_library.py'.")

    def launch_assistant(self):
        if NeuralAssistant:
            self.ai_window = NeuralAssistant()
            self.ai_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Could not find 'neural_assistant.py'.")

    def toggle_ai(self):
        if not ConfigManager:
            QMessageBox.critical(self, "Error", "ConfigManager not loaded.")
            return

        current_state = ConfigManager.is_ai_enabled()
        new_state = not current_state
        ConfigManager.set_ai_enabled(new_state)
        
        self.update_ui_state()
        
        state_str = "ENABLED" if new_state else "DISABLED"
        QMessageBox.information(self, "AI Module", f"Neural Assistant is now {state_str}.\nPlease restart other modules to apply changes.")

    def update_ui_state(self):
        if ConfigManager:
            enabled = ConfigManager.is_ai_enabled()
            self.btn_ai.setEnabled(enabled)
            self.btn_ai.setText(f"🤖   Neural Assistant {'(Active)' if enabled else '(Inactive)'}")
            self.btn_toggle.setText(f"{'Disable' if enabled else 'Enable'} AI Module")
            
            # Update style to reflect state
            if enabled:
                self.btn_ai.setStyleSheet("") # Default
            else:
                 self.btn_ai.setStyleSheet("color: #555555; border: 1px dashed #3e3e42;")

# --- Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GenesisLauncher()
    window.show()
    sys.exit(app.exec())