import sys
import os
import ctypes
import time

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
                                 QWidget, QLabel, QPushButton, QMessageBox, QProgressDialog)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QIcon, QFont, QColor
    try:
        from src.utils.assets import resource_path
    except ImportError:
         def resource_path(p): return p
except ImportError:
    show_error_and_exit("PyQt6")

# --- Import your existing tool ---
# Ensure current directory is in path
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

try:
    from workflow_organizer import SmartWorkflowOrganizer
    from script_library import ScriptLibrary
    from src.ai.assistant import NeuralAssistant
    from config_manager import ConfigManager
    from src.version import UPDATE_JSON_URL, APP_VERSION
    from src.utils.updater import UpdateManager
except ImportError as e:
    SmartWorkflowOrganizer = None
    ScriptLibrary = None
    NeuralAssistant = None
    ConfigManager = None
    print(f"Import Error: {e}")

# --- WORKER THREADS ---
class UpdateCheckThread(QThread):
    finished = pyqtSignal(bool, str, str, str) # has_update, version, url, notes

    def run(self):
        try:
            updater = UpdateManager(UPDATE_JSON_URL)
            has_update, new_ver, url, notes = updater.check_for_updates()
            self.finished.emit(has_update, new_ver, url, notes)
        except Exception as e:
            print(f"Update check failed: {e}")
            self.finished.emit(False, "", "", "")

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)

    def __init__(self, updater, url):
        super().__init__()
        self.updater = updater
        self.url = url

    def run(self):
        try:
            success = self.updater.download_update(self.url, self.report_progress)
            self.finished.emit(success)
        except Exception as e:
            print(f"Download error: {e}")
            self.finished.emit(False)

    def report_progress(self, percent):
        self.progress.emit(percent)

# --- MAIN LAUNCHER ---
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
        
        from PyQt6.QtWidgets import QGridLayout
        layout = QGridLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50) 

        # --- Header Section ---
        title = QLabel("PROJECT GENESIS")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 4px; color: white;") 
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 2) 
        
        subtitle = QLabel("Select a module to begin")
        subtitle.setStyleSheet("font-size: 18px; margin-bottom: 40px; color: #aaaaaa;") 
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle, 1, 0, 1, 2)

        # --- Buttons Section (Grid) ---
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

        # 4. Toggle AI
        self.btn_toggle = create_card_button("Enable AI", "⚡", self.toggle_ai)
        layout.addWidget(self.btn_toggle, 3, 1)

        # Footer
        self.lbl_footer = QLabel(f"System v{APP_VERSION} | Checking for updates...")
        self.lbl_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_footer.setStyleSheet("font-size: 12px; color: #888; margin-top: 20px;")
        layout.addWidget(self.lbl_footer, 4, 0, 1, 2)
        
        # Center the grid
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_ai_ref = self.btn_ai
        self.update_ui_state()
        
        self.animate_fade_in()

        # Start Update Check
        QTimer.singleShot(100, self.start_update_check)

    def animate_fade_in(self):
        try:
            from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
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

    # --- UPDATE LOGIC ---
    def start_update_check(self):
        self.update_thread = UpdateCheckThread()
        self.update_thread.finished.connect(self.on_update_checked)
        self.update_thread.start()

    def on_update_checked(self, has_update, version, url, notes):
        if has_update:
            self.lbl_footer.setText(f"System v{APP_VERSION} | Update Available: v{version}")
            self.lbl_footer.setStyleSheet("font-size: 12px; color: #00cc66; font-weight: bold; margin-top: 20px;")
            
            msg = f"A new version ({version}) is available!\n\nRelease Notes:\n{notes}\n\nDo you want to update now?"
            reply = QMessageBox.question(self, "Update Available", msg, 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.perform_update(url)
        else:
            self.lbl_footer.setText(f"System v{APP_VERSION} | Up to date")

    def perform_update(self, url):
        self.progress_dlg = QProgressDialog("Downloading update...", "Cancel", 0, 100, self)
        self.progress_dlg.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dlg.setMinimumDuration(0)
        self.progress_dlg.setValue(0)
        
        updater = UpdateManager(UPDATE_JSON_URL)
        
        self.download_thread = DownloadThread(updater, url)
        self.download_thread.progress.connect(self.progress_dlg.setValue)
        self.download_thread.finished.connect(lambda success: self.on_download_finished(success, updater))
        self.download_thread.start()

    def on_download_finished(self, success, updater):
        if success:
            self.progress_dlg.setLabelText("Installing update...")
            self.progress_dlg.setValue(100)
            # Give UI a moment to show 100%
            QTimer.singleShot(500, lambda: self.finalize_update(updater))
        else:
            self.progress_dlg.close()
            QMessageBox.critical(self, "Update Failed", "Failed to download the update.\nPlease check your internet connection.")

    def finalize_update(self, updater):
        self.progress_dlg.close()
        # This will restart the app
        updater.restart_and_install()

    # --- LAUNCHERS ---
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
            
            if enabled:
                pass 
            else:
                 self.btn_ai_ref.setStyleSheet("QPushButton { background-color: rgba(30, 30, 30, 0.5); color: #555; border: 2px dashed #444; border-radius: 12px; font-size: 18px; font-weight: bold; }")

if __name__ == "__main__":
    from src.utils.logger import CrashHandler
    CrashHandler.setup()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = GenesisLauncher()
    window.show()
    sys.exit(app.exec())