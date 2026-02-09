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
    from PyQt6.QtGui import QFont, QColor, QIcon
    try:
        from src.utils.assets import resource_path
    except ImportError:
         def resource_path(p): return p
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
        
        # Set Window Icon
        try:
            icon_path = resource_path("assets/icon.bmp")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

        # Apply Theme
        self.apply_theme()

        # Central Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Use Grid Layout for Hub Design
        from PyQt6.QtWidgets import QGridLayout
        layout = QGridLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50) 

        # --- Header Section ---
        title = QLabel("PROJECT GENESIS")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 4px; color: white;") 
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 2) # Span 2 columns
        
        subtitle = QLabel("Select a module to begin")
        subtitle.setStyleSheet("font-size: 18px; margin-bottom: 40px; color: #aaaaaa;") 
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle, 1, 0, 1, 2)

        # --- Buttons Section (Grid) ---
        # Helper to create big buttons
        def create_card_button(text, icon, callback):
            btn = QPushButton(f"{icon}\n\n{text}")
            btn.setFixedSize(250, 180)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px; font-weight: bold;
                    border-radius: 12px;
                    border: 2px solid #444;
                    background-color: rgba(60, 60, 65, 0.6);
                    color: white;
                }
                QPushButton:hover {
                    background-color: rgba(80, 80, 90, 0.8);
                    border: 2px solid #007acc;
                }
            """)
            btn.clicked.connect(callback)
            return btn

        # 1. Workflow
        btn_workflow = create_card_button("Workflow", "📂", self.launch_workflow)
        layout.addWidget(btn_workflow, 2, 0)

        # 2. Script Library
        btn_scripts = create_card_button("Script Library", "📜", self.launch_library) 
        layout.addWidget(btn_scripts, 2, 1)

        # 3. Neural Assistant
        self.btn_ai = create_card_button("Neural Assistant", "🤖", self.launch_assistant)
        layout.addWidget(self.btn_ai, 3, 0)

        # 4. Settings / Toggle
        # Grouping Settings and Toggle for the 4th slot? Or just Toggle?
        # Let's make the 4th slot a "System" card that toggles AI or opens Settings?
        # For now, sticking to the plan: Toggle AI. 
        # But wait, we need Settings access too! 
        # Let's add a small settings button in corner, and use 4th slot for Toggle AI?
        
        self.btn_toggle = create_card_button("Enable AI", "⚡", self.toggle_ai)
        layout.addWidget(self.btn_toggle, 3, 1)

        # Footer
        footer = QLabel("System v2.0 | Ready")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("font-size: 12px; color: #666; margin-top: 20px;")
        layout.addWidget(footer, 4, 0, 1, 2)
        
        # Center the grid in the window
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_ai_ref = self.btn_ai # Keep ref for updates
        self.update_ui_state()
        
        self.animate_fade_in()

    def animate_fade_in(self):
        try:
            from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
            
            # Opacity Effect
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
            self.opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self.opacity_effect)
            
            self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.anim.setDuration(800)
            self.anim.setStartValue(0)
            self.anim.setEndValue(1)
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.anim.start()
        except ImportError:
            pass

    def launch_workflow(self):
        try:
            from src.workflow_organizer import SmartWorkflowOrganizer
            self.workflow_window = SmartWorkflowOrganizer()
            self.workflow_window.show()
            self.close()
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"Could not load Workflow Organizer: {e}")

    def launch_library(self):
        try:
            from src.script_library import ScriptLibrary
            self.library_window = ScriptLibrary()
            self.library_window.show()
            self.close()
        except ImportError as e:
             QMessageBox.critical(self, "Error", f"Could not load Script Library: {e}")
        
    def launch_assistant(self):
        try:
            from src.ai.assistant import NeuralAssistant
            self.assistant_window = NeuralAssistant()
            self.assistant_window.show()
        except ImportError:
            QMessageBox.warning(self, "Module Missing", "Neural Assistant module not found.")

    def toggle_ai(self):
        if ConfigManager:
            enabled = not ConfigManager.is_ai_enabled()
            ConfigManager.set_ai_enabled(enabled)
            self.update_ui_state()
            
            status = "Enabled" if enabled else "Disabled"
            QMessageBox.information(self, "AI Module", f"Neural Assistant {status}.")
            
    def apply_theme(self):
        try:
            if ConfigManager:
                cfg = ConfigManager._get_shared_instance()
                theme_name = cfg.get_theme()
                use_gradient = cfg.is_gradient_enabled()
                from src.themes import ThemeManager
                stylesheet = ThemeManager.get_stylesheet(theme_name, use_gradient)
                
                app = QApplication.instance()
                if app:
                    app.setStyle("Fusion")
                    app.setStyleSheet(stylesheet)
                else:
                    self.setStyleSheet(stylesheet)

        except Exception as e:
            print(f"Error applying theme: {e}")

    def update_ui_state(self):
        if ConfigManager:
            enabled = ConfigManager.is_ai_enabled()
            self.btn_ai_ref.setEnabled(enabled)
            self.btn_ai_ref.setText(f"🤖\n\nNeural Assistant\n{' (Active)' if enabled else ' (Inactive)'}")
            self.btn_toggle.setText(f"⚡\n\n{'Disable' if enabled else 'Enable'} AI")
            
            # Update style to reflect state
            if enabled:
                # Default style is already set in create_card_button
                pass 
            else:
                 self.btn_ai_ref.setStyleSheet("QPushButton { background-color: rgba(30, 30, 30, 0.5); color: #555; border: 2px dashed #444; border-radius: 12px; font-size: 18px; font-weight: bold; }")

# --- Entry Point ---
if __name__ == "__main__":
    from src.utils.logger import CrashHandler
    CrashHandler.setup()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = GenesisLauncher()
    window.show()
    sys.exit(app.exec())