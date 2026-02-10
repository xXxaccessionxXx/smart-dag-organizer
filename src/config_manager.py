import os
import json
import shutil
from src.themes import ThemeManager

class ConfigManager:
    def __init__(self, config_file="config.json"):
        # Resolve to AppData to prevent CWD pollution (e.g. Desktop)
        app_data = self.get_app_data_dir()
        self.config_file = os.path.join(app_data, config_file)
        self.config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = {}
        else:
            self.config = {}

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def get_app_data_dir(self):
        # Use APPDATA for persistence across updates
        app_data = os.environ.get('APPDATA')
        if not app_data:
             app_data = os.path.expanduser("~")
             
        base_dir = os.path.join(app_data, "SmartDAGOrganizer")
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    def get_data_path(self):
        base_dir = self.get_app_data_dir()
        return os.path.join(base_dir, "genesis_data.json")

    @staticmethod
    def _get_shared_instance():
        return ConfigManager()

    @staticmethod
    def is_ai_enabled():
        cfg = ConfigManager._get_shared_instance()
        return cfg.get("ai_enabled", True) # Default to True

    @staticmethod
    def set_ai_enabled(enabled):
        cfg = ConfigManager._get_shared_instance()
        cfg.set("ai_enabled", enabled)

    def get_theme(self):
        return self.get("theme", "Dark")

    def get_hover_persistence(self):
        return self.get("hover_persistence", True)

    def get_auto_save_interval(self):
        return self.get("auto_save_interval", 300)

    def get_grid_style(self):
        return self.get("grid_style", "Lines") # Options: Lines, Dots

    def get_theme_data(self):
        from src.themes import ThemeManager
        theme_name = self.get_theme()
        t = ThemeManager.get_theme(theme_name)
        return t

    def is_gradient_enabled(self):
        return self.get("use_gradient", False)

    def set_gradient_enabled(self, enabled):
        self.set("use_gradient", enabled)

    def get_window_geometry(self):
        return self.get("window_geometry", None)

    def set_window_geometry(self, geometry_hex):
        self.set("window_geometry", geometry_hex)
