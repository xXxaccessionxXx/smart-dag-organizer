import os
import json
from src.config_manager import ConfigManager

class IntegrationManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.integrations = {}
        self.config_manager = ConfigManager._get_shared_instance()
        self.credentials_path = os.path.join(self.config_manager.get_app_data_dir(), "credentials.json")
        self.token_path = os.path.join(self.config_manager.get_app_data_dir(), "token.json")

    def register_integration(self, integration_cls):
        """Instantiates and registers an integration."""
        instance = integration_cls(self)
        self.integrations[instance.id] = instance

    def get_integration(self, integration_id):
        return self.integrations.get(integration_id)

    def get_all_integrations(self):
        return self.integrations.values()
    
    def get_credentials_path(self):
        return self.credentials_path
    
    def get_token_paths(self):
         return self.token_path
