
import sys
import os
import zipfile
import shutil
import subprocess
from PyQt6.QtWidgets import (QApplication, QWizard, QWizardPage, QVBoxLayout, QLabel, 
                             QProgressBar, QMessageBox, QCheckBox)
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

class IntroPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(f"Welcome to the {APP_NAME} Setup")
        
        layout = QVBoxLayout()
        label = QLabel(f"This wizard will install {APP_NAME} on your computer.\n\n"
                       f"Destination: {INSTALL_DIR}\n\n"
                       "Click Next to continue.")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)

class InstallPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Installing...")
        self.setCommitPage(True) # Removes Cancel/Back once started
        
        layout = QVBoxLayout()
        self.status_label = QLabel("Ready to install...")
        layout.addWidget(self.status_label)
        
        self.pbar = QProgressBar()
        layout.addWidget(self.pbar)
        
        self.setLayout(layout)
        
    def initializePage(self):
        # Start installation automatically when entering this page
        self.start_install()

    def start_install(self):
        self.thread = InstallThread()
        self.thread.progress.connect(self.pbar.setValue)
        self.thread.status.connect(self.status_label.setText)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, success, message):
        if success:
            self.status_label.setText("Installation Successful!")
            self.pbar.setValue(100)
            self.wizard().next()
        else:
            self.status_label.setText(f"Error: {message}")
            QMessageBox.critical(self, "Installation Failed", message)

class FinishPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Installation Complete")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"{APP_NAME} has been successfully installed."))
        
        self.chk_launch = QCheckBox(f"Launch {APP_NAME}")
        self.chk_launch.setChecked(True)
        layout.addWidget(self.chk_launch)
        
        self.chk_desktop = QCheckBox("Create Desktop Shortcut")
        self.chk_desktop.setChecked(True)
        layout.addWidget(self.chk_desktop)
        
        self.setLayout(layout)

    def validatePage(self):
        # Create Shortcuts
        exe_path = os.path.join(INSTALL_DIR, "SmartDAGOrganizer", EXE_NAME)
        if not os.path.exists(exe_path):
             exe_path = os.path.join(INSTALL_DIR, EXE_NAME) # Check root if dist structure differs

        if self.chk_desktop.isChecked():
            self.create_shortcut(exe_path, "Desktop")
            
        # Create Start Menu Shortcut (Always)
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
            # Fallback using VBScript if pywin32 not installed
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
        self.setFixedSize(600, 400)
        
        self.addPage(IntroPage())
        self.addPage(InstallPage())
        self.addPage(FinishPage())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Try to verify payload exists before showing UI
    # but let the UI handle the actual error for better UX
    
    wizard = SetupWizard()
    wizard.show()
    sys.exit(app.exec())
