
import os
import shutil
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QHBoxLayout, QFileDialog, QMessageBox,
                             QTabWidget, QWidget, QCheckBox, QSpinBox, QComboBox)
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Settings")
        self.resize(600, 400)
        self.setModal(True)
        
        # Styling
        self.setStyleSheet("""
            QDialog { background-color: #2D2D30; color: white; }
            QLabel { color: #d4d4d4; font-size: 12px; }
            QLineEdit, QSpinBox, QComboBox { 
                background-color: #3e3e42; color: white; 
                padding: 5px; border: 1px solid #555; border-radius: 4px;
            }
            QTabWidget::pane { border: 1px solid #3e3e42; }
            QTabBar::tab {
                background: #2D2D30; color: #d4d4d4; padding: 8px 12px;
                border: 1px solid #3e3e42; border-bottom: none;
            }
            QTabBar::tab:selected { background: #3e3e42; color: white; }
            QPushButton { 
                background-color: #007acc; color: white; border: none; 
                padding: 6px 12px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #0062a3; }
            QPushButton#cancel { background-color: #3e3e42; }
            QPushButton#cancel:hover { background-color: #555; }
        """)

        layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.create_general_tab()
        self.create_appearance_tab()
        self.create_behavior_tab()

        # Footer Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("Save & Apply")
        self.btn_save.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)

    def create_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Data Location
        lbl_location = QLabel("Data Storage Location:")
        layout.addWidget(lbl_location)
        
        path_layout = QHBoxLayout()
        self.txt_path = QLineEdit()
        self.txt_path.setText(self.config_manager.get_data_path())
        self.txt_path.setReadOnly(True) 
        path_layout.addWidget(self.txt_path)
        
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self.browse_folder)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)
        
        lbl_hint = QLabel("Select a folder (e.g., OneDrive, Dropbox) to sync your project across devices.")
        lbl_hint.setStyleSheet("color: #888888; font-style: italic;")
        lbl_hint.setWordWrap(True)
        layout.addWidget(lbl_hint)
        
        layout.addStretch()
        self.tabs.addTab(tab, "General")

    def create_appearance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme
        lbl_theme = QLabel("Theme:")
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Dark", "Light (Coming Soon)"])
        current_theme = self.config_manager.get_theme()
        index = self.combo_theme.findText(current_theme)
        if index >= 0:
            self.combo_theme.setCurrentIndex(index)
        layout.addWidget(lbl_theme)
        layout.addWidget(self.combo_theme)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Appearance")

    def create_behavior_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Hover Persistence
        self.chk_hover = QCheckBox("Keep Note Popup Open on Hover")
        self.chk_hover.setChecked(self.config_manager.get_hover_persistence())
        self.chk_hover.setStyleSheet("color: white;")
        layout.addWidget(self.chk_hover)
        
        layout.addSpacing(10)
        
        # Auto-Save
        lbl_autosave = QLabel("Auto-Save Interval (seconds):")
        self.spin_autosave = QSpinBox()
        self.spin_autosave.setRange(10, 3600)
        self.spin_autosave.setValue(int(self.config_manager.get_auto_save_interval()))
        layout.addWidget(lbl_autosave)
        layout.addWidget(self.spin_autosave)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Behavior")

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Data Folder")
        if folder:
            full_path = os.path.join(folder, "genesis_data.json")
            self.txt_path.setText(full_path)

    def save_settings(self):
        # 1. Data Path
        new_path = self.txt_path.text()
        current_path = self.config_manager.get_data_path()
        path_changed = False
        
        if new_path != current_path:
            # Check migration
            if os.path.exists(current_path) and not os.path.exists(new_path):
                reply = QMessageBox.question(self, "Migrate Data?", 
                                             "Do you want to move your existing data to the new location?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        shutil.copy2(current_path, new_path)
                    except Exception as e:
                        QMessageBox.warning(self, "Migration Error", f"Could not copy data: {e}")
                        return
            
            self.config_manager.set("data_path", new_path)
            path_changed = True

        # 2. Appearance
        theme = self.combo_theme.currentText()
        if "Light" in theme: theme = "Light" # Handle "(Coming Soon)"
        else: theme = "Dark"
        self.config_manager.set("theme", theme)

        # 3. Behavior
        self.config_manager.set("hover_persistence", self.chk_hover.isChecked())
        self.config_manager.set("auto_save_interval", self.spin_autosave.value())

        # Finish
        QMessageBox.information(self, "Settings Saved", "Settings applied successfully.")
        self.accept()
