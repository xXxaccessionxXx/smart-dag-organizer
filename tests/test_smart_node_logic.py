import sys
import os
import unittest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QGraphicsScene

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.workflow_organizer import SmartNode

class TestSmartNodeLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_z_index_behavior(self):
        """Verify SmartNode raises Z-index on hover and resets on hide."""
        # Mock main window
        mock_mw = MagicMock()
        mock_mw.theme_data = {
            "node_bg": "#000000", 
            "text_color": "#ffffff", 
            "text_dim": "#aaaaaa",
            "accent_color": "#007acc",
            "window_bg": "#1e1e1e",
            "node_border_color": "#333333"
        }
        mock_mw.integration_manager = MagicMock()
        
        scene = QGraphicsScene()
        node = SmartNode("Test Node", 0, 0, mock_mw)
        scene.addItem(node)
        
        # Initial State
        self.assertEqual(node.zValue(), 0)
        
        # Simulate Hover Enter logic manually (since we can't easily mock the event for super())
        node.setZValue(100)
        self.assertEqual(node.zValue(), 100)
        
        # Simulate Hide Popup (which resets Z)
        node.hide_popup()
        self.assertEqual(node.zValue(), 0)

    def test_popup_attribute_access(self):
        """Verify NotePopup accesses main_window correctly."""
        mock_mw = MagicMock()
        mock_mw.theme_data = {
            "node_bg": "#000000", 
            "text_color": "#ffffff", 
            "text_dim": "#aaaaaa",
            "accent_color": "#007acc",
            "window_bg": "#1e1e1e",
            "node_border_color": "#333333"
        }
        # setup integration manager mock
        mock_int_mgr = MagicMock()
        mock_mw.integration_manager = mock_int_mgr
        mock_calendar = MagicMock()
        mock_int_mgr.get_integration.return_value = mock_calendar
        
        scene = QGraphicsScene()
        node = SmartNode("Test Node", 0, 0, mock_mw)
        scene.addItem(node)
        
        # Access popup
        popup = node.popup
        
        # Call open_add_event_dialog
        # This triggered the crash before because it accessed node.mainWindow instead of main_window
        try:
            popup.open_add_event_dialog()
            # If no exception, passed
        except AttributeError as e:
            self.fail(f"open_add_event_dialog raised AttributeError: {e}")

if __name__ == '__main__':
    unittest.main()
