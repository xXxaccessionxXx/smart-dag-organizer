import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsProxyWidget

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.workflow_organizer import SmartNode, SmartWorkflowOrganizer

class TestNotePersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_html_persistence(self):
        # Mock Window
        class MockWindow:
            theme_data = {
                "node_bg": "#333333", 
                "text_dim": "#888888", 
                "text_color": "#ffffff",
                "accent_color": "#007acc",
                "window_bg": "#1e1e1e",
                "grid_light": "#2d2d30",
                "node_border_color": "#444"
            }
            def config_manager(self): pass
            
        mock_window = MockWindow()
        
        # Create Node
        node = SmartNode("Test Node", 0, 0, mock_window)
        
        # Simulate bold text HTML
        html_content = '<html><body><p><span style=" font-weight:600;">Bold Text</span></p></body></html>'
        
        # Set notes via popup logic (which we changed to use setHtml/toHtml)
        node.popup.txt_notes.setHtml(html_content)
        
        # Trigger update from popup
        node.update_notes_from_popup(node.popup.txt_notes.toHtml())
        
        # Verify node.notes contains the HTML
        self.assertIn("Bold Text", node.notes)
        self.assertIn("font-weight:600", node.notes) # QT uses 600 for bold in HTML output usually
        
        # Verify to_dict preserves it
        data = node.to_dict()
        self.assertEqual(data["notes"], node.notes)

if __name__ == '__main__':
    unittest.main()
