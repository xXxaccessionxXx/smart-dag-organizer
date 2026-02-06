
import sys
import os
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from PyQt6.QtCore import Qt, QEvent, QPointF
from PyQt6.QtGui import QKeyEvent

sys.path.append(os.getcwd())
app = QApplication(sys.argv)

from src.workflow_organizer import SmartNode, SmartView

class MockWindow:
    def focus_camera_on_nodes(self):
        print("Camera Focus Triggered")

def run_test():
    scene = QGraphicsScene()
    window = MockWindow()
    view = SmartView(scene, window)
    
    node = SmartNode("Test Node", 0, 0, None)
    scene.addItem(node)
    
    # Show Popup and Focus Text Edit
    node.popup.update_content("Node", "None", "", "")
    node.popup.setVisible(True)
    
    # We need to set focus on the ProxyWidget
    # verifying that the node.popup is indeed a QGraphicsProxyWidget
    proxy = node.popup
    
    # In a real app, clicking the text edit sets focus. 
    # We simulate this by setting the scene's focus item.
    scene.setFocusItem(proxy)
    
    # Simulate Space Key Press on View
    event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier, " ")
    
    print(f"TEST DEBUG: Scene Focus Item: {scene.focusItem()}")
    print("Simulating Space Press...")
    sys.stdout.flush()
    view.keyPressEvent(event)
    
    # If the text edit got the event, the text should have a space (if we could fully simulate the pipeline)
    # But since we are calling view.keyPressEvent directly, if it calls super(), the event propagates to scene -> focusItem.
    # If it calls focus_camera_on_nodes, it consumed it.
    
    # Ideally we'd mock focus_camera_on_nodes to fail the test if called.
    # But since we passed a MockWindow, we can check a flag? 
    # Be careful, MockWindow instance above is used.
    
    # Actually, simpler: check if the text changed? 
    # Calling view.keyPressEvent(event) -> if it calls super(), eventually it goes to the proxy, which forwards to widget.
    # So if text changes, we are good.
    
    current_text = node.popup.txt_notes.toPlainText()
    if " " in current_text:
         print("PASS: Space detected (unexpected if bug exists)")
    else:
         print("Initial Check: No space yet")

    # Let's redefine mock to crash or print
    # We can rely on the fact that if IT IS intercepted, the text WON'T change.
    # But to be sure it IS intercepted, we should see "Camera Focus Triggered" in output.
    
    # Note: QGraphicsProxyWidget event forwarding is complex. 
    # Direct KeyPress on View -> Scene -> Item.
    # If View eats it, Scene never sees it.
    
    if node.popup.txt_notes.toPlainText() == " ":
        print("PASS: Space key reached text edit")
    else:
        print("FAIL: Space key did not reach text edit (or logic is flawed)")

if __name__ == "__main__":
    run_test()
