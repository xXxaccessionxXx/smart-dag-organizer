import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QGraphicsScene

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock StatusChecker before importing workflow_organizer to avoid thread starting
sys.modules['src.utils.status_checker'] = MagicMock()

from src.workflow_organizer import SmartNode, SmartWorkflowOrganizer

class TestAsyncStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_status_update_flow(self):
        """Verify update_all_nodes triggers checker and apply_status_updates updates nodes."""
        # Create Organizer (mocks StatusChecker internally due to our sys.modules hack or we patch it)
        
        # Actually, cleaner to patch where it's used
        with patch('src.workflow_organizer.StatusChecker') as MockChecker:
            organizer = SmartWorkflowOrganizer()
            mock_worker = organizer.status_checker
            
            # Create a node
            mock_mw = MagicMock()
            mock_mw.theme_data = {
                "node_bg": "#000000", "text_color": "#ffffff", "text_dim": "#aaaaaa",
                "accent_color": "#007acc", "window_bg": "#1e1e1e", "node_border_color": "#333333"
            }
            organizer.main_window = mock_mw # Mock parent dependency if needed
            
            node = SmartNode("File Node", 0, 0, mock_mw)
            node.watch_path = "C:/fake/path.txt"
            node.file_exists = False
            organizer.nodes.append(node)
            
            # 1. Test update_all_nodes -> set_paths
            mock_worker.isRunning.return_value = True
            organizer.update_all_nodes()
            
            mock_worker.set_paths.assert_called_with(["C:/fake/path.txt"])
            
            # 2. Test apply_status_updates -> node update
            results = {"C:/fake/path.txt": True}
            organizer.apply_status_updates(results)
            
            self.assertTrue(node.file_exists)
            
            # 3. Test apply_status_updates -> false
            results = {"C:/fake/path.txt": False}
            organizer.apply_status_updates(results)
            
            self.assertFalse(node.file_exists)

if __name__ == '__main__':
    unittest.main()
