import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.integrations.manager import IntegrationManager
from src.integrations.google_calendar import GoogleCalendarIntegration
from src.workflow_organizer import SmartWorkflowOrganizer

class TestIntegrations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create app instance for Qt
        cls.app = QApplication(sys.argv)

    def test_manager_registration(self):
        # Mock main window
        class MockWindow:
            pass
        
        manager = IntegrationManager(MockWindow())
        manager.register_integration(GoogleCalendarIntegration)
        
        integration = manager.get_integration("google_calendar")
        self.assertIsNotNone(integration)
        self.assertEqual(integration.name, "Google Calendar")
        self.assertIsInstance(integration, GoogleCalendarIntegration)
        
    def test_calendar_methods(self):
         # Mock manager
        class MockManager:
            credentials_path = "dummy_creds.json"
            token_path = "dummy_token.json"
            
        integration = GoogleCalendarIntegration(MockManager())
        self.assertEqual(integration.id, "google_calendar")
        
        # Should be false as files don't exist
        self.assertFalse(integration.is_configured())

if __name__ == '__main__':
    unittest.main()
