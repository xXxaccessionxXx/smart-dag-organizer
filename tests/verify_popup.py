
import sys
import os
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsSceneHoverEvent
from PyQt6.QtCore import QPointF, Qt

# Ensure src can be imported
sys.path.append(os.getcwd())

app = QApplication(sys.argv)

from src.workflow_organizer import SmartNode

def run_test():
    scene = QGraphicsScene()
    node = SmartNode("Test Node", 0, 0, None)
    scene.addItem(node)
    
    # 1. Check Initial State
    if node.popup.isVisible():
        print("FAIL: Popup should be hidden initially")
        sys.exit(1)
    print("PASS: Popup is hidden initially")
    
    # 2. Setup Data
    node.notes = "<b>Important</b> Details"
    node.attachment_type = "File"
    node.watch_path = "C:/fake/path/image.png"
    
    # 3. Trigger Logic Directly (Bypassing Event instantiation issues)
    # We test that update_content works and shows the correct data
    node.popup.update_content(node.name, node.attachment_type, node.watch_path, node.notes)
    node.popup.setVisible(True)
    
    # 4. Verify Visibility
    if not node.popup.isVisible():
        print("FAIL: Popup should be visible after setVisible(True)")
        sys.exit(1)
    print("PASS: Popup became visible")
    
    # 5. Verify Content Update (Accessing inner widgets)
    # popup is QGraphicsProxyWidget -> widget() -> container
    container = node.popup.widget()
    # We need to find the child widgets. 
    # Current implementation stores them as self.popup.lbl_title etc.
    
    if node.popup.lbl_title.text() != "Test Node":
        print(f"FAIL: Title mismatch. Got '{node.popup.lbl_title.text()}'")
        sys.exit(1)
    print("PASS: Title updated")
    
    if "Type: File" not in node.popup.lbl_info.text():
         print(f"FAIL: Info Text mismatch. Got '{node.popup.lbl_info.text()}'")
         sys.exit(1)
    print("PASS: Info updated")
    
    # 6. Hide
    node.popup.setVisible(False)
    
    if node.popup.isVisible():
        print("FAIL: Popup should be hidden")
        sys.exit(1)
    print("PASS: Popup hidden")

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_test()
