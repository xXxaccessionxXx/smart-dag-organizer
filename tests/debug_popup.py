import sys
import os
import traceback
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QGraphicsScene

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.workflow_organizer import SmartNode

def run_debug():
    app = QApplication.instance() or QApplication(sys.argv)
    
    mock_mw = MagicMock()
    mock_mw.theme_data = {
        "node_bg": "#000000", 
        "text_color": "#ffffff", 
        "text_dim": "#aaaaaa",
        "accent_color": "#007acc",
        "window_bg": "#1e1e1e",
        "node_border_color": "#333333"
    }
    mock_int_mgr = MagicMock()
    mock_mw.integration_manager = mock_int_mgr
    
    # Mock Calendar Integration
    mock_calendar = MagicMock()
    # Ensure get_integration returns something truthy and configured
    mock_int_mgr.get_integration.return_value = mock_calendar
    mock_calendar.is_configured.return_value = True
    mock_calendar.list_upcoming_events.return_value = []

    scene = QGraphicsScene()
    try:
        print("Creating SmartNode...")
        node = SmartNode("Test Node", 0, 0, mock_mw)
        scene.addItem(node)
        
        print("Accessing popup...")
        popup = node.popup
        
        print("Calling open_add_event_dialog...")
        popup.open_add_event_dialog()
        print("Success!")
        
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    run_debug()
