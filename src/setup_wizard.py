
import sys
import os
import zipfile
import shutil
import subprocess
from PyQt6.QtWidgets import (QApplication, QWizard, QWizardPage, QVBoxLayout, QLabel, 
                             QProgressBar, QMessageBox, QCheckBox, QWidget, QHBoxLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap

# Constants
APP_NAME = "Smart DAG Organizer"
INSTALL_DIR = os.path.join(os.environ['LOCALAPPDATA'], "SmartDAGOrganizer")
EXE_NAME = "SmartDAGOrganizer.exe"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class InstallThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def run(self):
        try:
            zip_path = resource_path("payload.zip")
            
            if not os.path.exists(zip_path):
                # Fallback for dev testing
                zip_path = "SmartDAG_Portable.zip"
                if not os.path.exists(zip_path):
                    self.finished_signal.emit(False, f"Payload not found at: {zip_path}")
                    return

            self.status.emit("Checking for existing data...")
            # --- DATA PRESERVATION START ---
            import tempfile
            backup_dir = os.path.join(tempfile.gettempdir(), "SmartDAG_Backup")
            has_backup = False
            
            if os.path.exists(INSTALL_DIR):
                try:
                    if os.path.exists(backup_dir):
                        shutil.rmtree(backup_dir)
                    os.makedirs(backup_dir)
                    
                    # Backup 'data' folder
                    data_src = os.path.join(INSTALL_DIR, "data")
                    if os.path.exists(data_src):
                        shutil.copytree(data_src, os.path.join(backup_dir, "data"))
                        has_backup = True
                        
                    # Backup 'config.json'
                    config_src = os.path.join(INSTALL_DIR, "config.json")
                    if os.path.exists(config_src):
                        shutil.copy2(config_src, backup_dir)
                        has_backup = True
                        
                except Exception as e:
                    print(f"Backup warning: {e}")
            # --- DATA PRESERVATION END ---

            self.status.emit("Cleaning up old files...")
            if os.path.exists(INSTALL_DIR):
                try:
                    shutil.rmtree(INSTALL_DIR)
                except Exception as e:
                    self.finished_signal.emit(False, f"Could not clean directory: {e}")
                    return
            
            os.makedirs(INSTALL_DIR, exist_ok=True)

            self.status.emit("Extracting files...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                total_files = len(zip_ref.infolist())
                for i, file in enumerate(zip_ref.infolist()):
                    zip_ref.extract(file, INSTALL_DIR)
                    self.progress.emit(int((i / total_files) * 90))
            
            # --- DATA RESTORE START ---
            if has_backup:
                self.status.emit("Restoring user data...")
                try:
                    # Restore 'data' folder (Overwrite templates)
                    backup_data = os.path.join(backup_dir, "data")
                    if os.path.exists(backup_data):
                        target_data = os.path.join(INSTALL_DIR, "data")
                        # shutil.copytree with dirs_exist_ok=True (Python 3.8+)
                        shutil.copytree(backup_data, target_data, dirs_exist_ok=True)
                        
                    # Restore 'config.json'
                    backup_config = os.path.join(backup_dir, "config.json")
                    if os.path.exists(backup_config):
                        shutil.copy2(backup_config, os.path.join(INSTALL_DIR, "config.json"))
                        
                    # Cleanup backup
                    shutil.rmtree(backup_dir)
                except Exception as e:
                     self.finished_signal.emit(False, f"Data Restore Failed: {e}")
                     return
            # --- DATA RESTORE END ---

            self.progress.emit(100)
            self.finished_signal.emit(True, "Installation Complete")

        except Exception as e:
            self.finished_signal.emit(False, str(e))

class Theme:
    # Modern Dark Theme Palette
    BG_COLOR = "#2D2D30"
    FG_COLOR = "#FFFFFF"
    ACCENT = "#007acc"
    ACCENT_HOVER = "#0062a3"
    SECONDARY_BG = "#3e3e42"
    BORDER = "#555555"
    
    STYLESHEET = f"""
        QWizard {{
            background-color: {BG_COLOR};
            color: {FG_COLOR};
        }}
        QWizardPage {{
            background-color: {BG_COLOR};
            color: {FG_COLOR};
        }}
        QLabel {{
            color: {FG_COLOR};
            font-size: 14px;
        }}
        QLabel#Title {{
            font-size: 24px;
            font-weight: bold;
            color: {ACCENT};
            margin-bottom: 20px;
        }}
        QLabel#Subtitle {{
            font-size: 16px;
            color: #dddddd;
            margin-bottom: 10px;
        }}
        QProgressBar {{
            border: 2px solid {BORDER};
            border-radius: 5px;
            text-align: center;
            background-color: {SECONDARY_BG};
            color: {FG_COLOR};
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background-color: {ACCENT};
            width: 20px;
        }}
        QPushButton {{
            background-color: {ACCENT};
            color: {FG_COLOR};
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}
        QPushButton:disabled {{
            background-color: {SECONDARY_BG};
            color: #888888;
        }}
        QCheckBox {{
            color: {FG_COLOR};
            font-size: 14px;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {BORDER};
            background: {SECONDARY_BG};
            border-radius: 3px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {ACCENT};
            border: 1px solid {ACCENT};
        }}
    """

class IntroPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("") # Hide default title, use custom layout
        self.setSubTitle("") 

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Custom Title
        title = QLabel(f"Welcome to {APP_NAME}")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(f"This wizard will guide you through the installation of {APP_NAME}.\n\n"
                      f"Destination: {INSTALL_DIR}\n\n"
                      "Click 'Next' to begin.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 16px; line-height: 1.5;")
        layout.addWidget(desc)
        
        layout.addStretch()
        
        # Note
        note = QLabel("Note: This software is provided as-is. Please report any issues on GitHub.")
        note.setStyleSheet("color: #888888; font-style: italic; font-size: 12px;")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(note)
        
        self.setLayout(layout)

class InstallPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("")
        self.setSubTitle("")
        self.setCommitPage(True) 
        
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Header
        header = QLabel("Installing...")
        header.setObjectName("Title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Status
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #aaaaaa;")
        layout.addWidget(self.status_label)
        
        # Progress Bar
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(30)
        layout.addWidget(self.pbar)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def initializePage(self):
        self.start_install()

    def start_install(self):
        self.thread = InstallThread()
        self.thread.progress.connect(self.pbar.setValue)
        self.thread.status.connect(self.status_label.setText)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, success, message):
        if success:
            self.status_label.setText("Success!")
            self.pbar.setValue(100)
            # Auto-advance after short delay? Or just let user click next.
            # QTimer.singleShot(1000, self.wizard().next)
            self.wizard().next()
        else:
            self.status_label.setText("Installation Failed")
            self.status_label.setStyleSheet("color: #ff5555; font-weight: bold; font-size: 18px;")
            QMessageBox.critical(self, "Error", message)

class FinishPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("")
        self.setSubTitle("")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QLabel("Installation Complete")
        header.setObjectName("Title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Icon/Checkmark placeholder (text for now)
        check = QLabel("✔")
        check.setStyleSheet("font-size: 60px; color: #4caf50; margin: 10px;")
        check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(check)
        
        desc = QLabel(f"{APP_NAME} has been successfully installed on your computer.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Options container for alignment
        opts_layout = QVBoxLayout()
        opts_layout.setSpacing(10)
        
        self.chk_launch = QCheckBox(f"Launch {APP_NAME}")
        self.chk_launch.setChecked(True)
        self.chk_launch.setCursor(Qt.CursorShape.PointingHandCursor)
        opts_layout.addWidget(self.chk_launch)
        
        self.chk_desktop = QCheckBox("Create Desktop Shortcut")
        self.chk_desktop.setChecked(True)
        self.chk_desktop.setCursor(Qt.CursorShape.PointingHandCursor)
        opts_layout.addWidget(self.chk_desktop)
        
        # Center options
        container = QWidget()
        container.setLayout(opts_layout)
        container.setFixedWidth(300)
        
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(container)
        h_layout.addStretch()
        
        layout.addLayout(h_layout)
        layout.addStretch()
        
        self.setLayout(layout)

    def validatePage(self):
        # Create Shortcuts
        exe_path = os.path.join(INSTALL_DIR, "SmartDAGOrganizer", EXE_NAME)
        if not os.path.exists(exe_path):
             exe_path = os.path.join(INSTALL_DIR, EXE_NAME)

        if self.chk_desktop.isChecked():
            self.create_shortcut(exe_path, "Desktop")
            
        self.create_shortcut(exe_path, "StartMenu")

        # Launch
        if self.chk_launch.isChecked():
            if os.path.exists(exe_path):
                subprocess.Popen([exe_path])
            else:
                 QMessageBox.warning(self, "Error", f"Could not find executable at:\n{exe_path}")

        return True

    def create_shortcut(self, target, location_type):
        try:
            import winshell
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            if location_type == "Desktop":
                location = shell.SpecialFolders("Desktop")
            else:
                location = shell.SpecialFolders("StartMenu")
            shortcut_path = os.path.join(location, f"{APP_NAME}.lnk")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.IconLocation = target
            shortcut.save()
        except ImportError:
             self.create_shortcut_vbs(target, location_type)

    def create_shortcut_vbs(self, target, location_type):
        vbs_script = f"""
        Set oWS = WScript.CreateObject("WScript.Shell")
        sLinkFile = oWS.SpecialFolders("{location_type}") & "\{APP_NAME}.lnk"
        Set oLink = oWS.CreateShortcut(sLinkFile)
        oLink.TargetPath = "{target}"
        oLink.WorkingDirectory = "{os.path.dirname(target)}"
        oLink.Save
        """
        vbs_path = os.path.join(INSTALL_DIR, "create_shortcut.vbs")
        with open(vbs_path, "w") as f:
            f.write(vbs_script)
        subprocess.call(['cscript', '//Nologo', vbs_path])
        os.remove(vbs_path)

class SetupWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} Setup")
        self.setFixedSize(700, 500)
        
        # Apply Theme
        self.setStyleSheet(Theme.STYLESHEET)
        
        # Wizard Options
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        
        # Hide default logo/watermark to use our custom full-page layouts
        self.setOption(QWizard.WizardOption.NoDefaultButton, False)
        
        # Add Pages
        self.addPage(IntroPage())
        self.addPage(InstallPage())
        self.addPage(FinishPage())
        
        # Customize Buttons
        self.setButtonText(QWizard.WizardButton.NextButton, "Next >")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Finish & Launch")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Cancel")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    wizard = SetupWizard()
    wizard.show()
    sys.exit(app.exec())
