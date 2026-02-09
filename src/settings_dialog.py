import os
import shutil
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QHBoxLayout, QFileDialog, QMessageBox,
                             QTabWidget, QWidget, QCheckBox, QSpinBox, QComboBox,
                             QFormLayout)
from PyQt6.QtCore import Qt

# Try Import ThemeManager safely
try:
    from src.themes import ThemeManager
except ImportError as e:
    print(f"Error importing ThemeManager in settings_dialog: {e}")
    ThemeManager = None

class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None, apply_callback=None):
        print("SettingsDialog.__init__ started")
        super().__init__(parent)
        self.config_manager = config_manager
        self.apply_callback = apply_callback
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
        
        print("Creating tabs...")
        self.create_general_tab()
        print("General tab created.")
        self.create_appearance_tab()
        print("Appearance tab created.")
        self.create_behavior_tab()
        print("Behavior tab created.")

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
        print("SettingsDialog.__init__ finished")

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
        
        form_layout = QFormLayout()
        
        # Theme
        lbl_theme = QLabel("Theme:")
        self.combo_theme = QComboBox()
        
        # Load themes dynamically
        if ThemeManager:
            theme_names = list(ThemeManager.THEMES.keys())
            self.combo_theme.addItems(theme_names)
        else:
            self.combo_theme.addItem("Dark") # Fallback
            
        self.combo_theme.currentIndexChanged.connect(self.trigger_live_update)
        
        current_theme = self.config_manager.get_theme()
        index = self.combo_theme.findText(current_theme)
        if index >= 0:
            self.combo_theme.setCurrentIndex(index)
        else:
            default_index = self.combo_theme.findText("Dark")
            if default_index >= 0: self.combo_theme.setCurrentIndex(default_index)

        # Grid Style
        lbl_grid = QLabel("Grid Style:")
        self.combo_grid = QComboBox()
        self.combo_grid.addItems(["Lines", "Dots"])
        
        current_grid = self.config_manager.get_grid_style()
        idx_grid = self.combo_grid.findText(current_grid)
        if idx_grid >= 0: self.combo_grid.setCurrentIndex(idx_grid)

        # Gradient
        self.chk_gradient = QCheckBox("Enable UI Gradients")
        self.chk_gradient.setChecked(self.config_manager.is_gradient_enabled())
        self.chk_gradient.stateChanged.connect(self.trigger_live_update)

        form_layout.addRow(lbl_theme, self.combo_theme)
        form_layout.addRow(lbl_grid, self.combo_grid)
        form_layout.addRow("", self.chk_gradient)

        layout.addLayout(form_layout)
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

    def trigger_live_update(self):
        """Applies settings immediately to the open window."""
        # 1. Update Config in memory (persistence handled on Save)
        # Actually, for "Live", we might need to persist or at least set the config 
        # so the callback (which likely calls config.get_theme()) sees the new value.
        # Let's set it. Cancellation reverting is out of scope for now unless we add it.
        
        theme = self.combo_theme.currentText()
        self.config_manager.set("theme", theme)
        
        use_gradient = self.chk_gradient.isChecked()
        self.config_manager.set_gradient_enabled(use_gradient)
        
        # 2. Trigger Callback
        if self.apply_callback:
            self.apply_callback()
            
        # 3. Update Self (Dialog) Style
        if ThemeManager:
            self.setStyleSheet(ThemeManager.get_stylesheet(theme, use_gradient))

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

        # 2. Appearance -- Already set by live update, but ensures saving to file
        theme = self.combo_theme.currentText()
        self.config_manager.set("theme", theme)
        
        grid_style = self.combo_grid.currentText()
        self.config_manager.set("grid_style", grid_style)

        use_gradient = self.chk_gradient.isChecked()
        self.config_manager.set_gradient_enabled(use_gradient)

        # 3. Behavior
        self.config_manager.set("hover_persistence", self.chk_hover.isChecked())
        self.config_manager.set("auto_save_interval", self.spin_autosave.value())

        # Finish
        QMessageBox.information(self, "Settings Saved", "Settings applied successfully.")
        self.accept()
