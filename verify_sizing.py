
import sys
import os
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from PyQt6.QtGui import QFont

# Ensure src in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

app = QApplication(sys.argv)

def test_dynamic_sizing():
    print("\n--- Testing Dynamic Node Sizing ---")
    try:
        from src.workflow_organizer import SmartNode, SmartWorkflowOrganizer
        # Mock window for theme data
        class MockWindow:
            theme_data = {
                "node_bg": "#333333",
                "accent_color": "#007acc", 
                "window_bg": "#1e1e1e",
                "text_dim": "#aaaaaa",
                "text_color": "#ffffff"
            }
            def config_manager(self): return None

        scene = QGraphicsScene()
        node = SmartNode("Short", 0, 0, MockWindow())
        scene.addItem(node)
        
        initial_width = node.rect().width()
        print(f"Initial Width ('Short'): {initial_width}")
        
        # Change text
        print("Changing text to long string...")
        node.text_item.setPlainText("This is a very long title for testing dynamic sizing")
        node.update_name_from_text() # Trigger manually as signal might not fire in script without loop
        
        new_width = node.rect().width()
        print(f"New Width: {new_width}")
        
        if new_width > initial_width:
            print("PASS: Node expanded.")
        else:
            print(f"FAIL: Node did not expand. {new_width} vs {initial_width}")

    except Exception as e:
        print(f"CRITICAL TEST FAIL: {e}")

if __name__ == "__main__":
    test_dynamic_sizing()
