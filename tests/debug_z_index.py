import sys
import os
import traceback
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from PyQt6.QtCore import QPointF

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
    mock_mw.integration_manager = MagicMock()
    
    scene = QGraphicsScene()
    node = SmartNode("Test Node", 0, 0, mock_mw)
    scene.addItem(node)
    
    print(f"Initial Z: {node.zValue()}")
    
    try:
        mock_event = MagicMock()
        # Mock pos() to return a valid QPointF
        mock_event.pos.return_value = QPointF(10, 10)
        
        print("Calling hoverEnterEvent...")
        node.hoverEnterEvent(mock_event)
        
        print(f"Post-Hover Z: {node.zValue()}")
        
        print("Calling hide_popup...")
        node.hide_popup()
        
        print(f"Final Z: {node.zValue()}")
        
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    run_debug()
