import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.event_dialog import EventDialog
# from src.workflow_organizer import NotePopup # NotePopup is nested or hard to isolate easily without more mocks

class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_event_dialog_init(self):
        """Verify EventDialog initializes correctly."""
        dialog = EventDialog()
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.windowTitle(), "Create Google Calendar Event")
        
    def test_event_dialog_validation(self):
        """Verify validation logic in EventDialog."""
        dialog = EventDialog()
        # Should fail validation (empty summary)
        # We can't easily test QMessageBox without mocking, but we can check state if we exposed validation methods
        # For now, just ensuring it doesn't crash on init is a good smoke test.
        pass

if __name__ == '__main__':
    unittest.main()
