import os
import json
import shutil
from src.themes import ThemeManager

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
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

    def get_data_path(self):
        # Default to 'data/genesis_data.json' relative to CWD if not set
        default_path = os.path.join("data", "genesis_data.json")
        path = self.get("data_path", default_path)
        
        # Ensure directory exists if it's the default one
        if path == default_path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
        return path

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
