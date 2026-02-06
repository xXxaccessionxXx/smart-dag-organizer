
import sys
import os
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer

sys.path.append(os.getcwd())
app = QApplication(sys.argv)

from src.workflow_organizer import SmartNode

def run_test():
    scene = QGraphicsScene()
    node = SmartNode("Interactive Node", 0, 0, None)
    scene.addItem(node)
    
    # 1. Test Note Sync
    print("Testing Note Sync...")
    node.popup.update_content("Node", "None", "", "")
    
    # Simulate typing in popup
    # We set text directly on the text edit
    node.popup.txt_notes.setPlainText("Hello World")
    
    # Check if node.notes updated
    if node.notes != "Hello World":
        print(f"FAIL: Node notes did not update. Got '{node.notes}'")
        sys.exit(1)
    print("PASS: Notes synced to Node")
    
    # 2. Test Open Attachment Logic (Mock)
    print("Testing Open Attachment Logic...")
    node.attachment_type = "File"
    # Create a dummy file
    with open("test_dummy.txt", "w") as f:
        f.write("dummy")
    node.watch_path = os.path.abspath("test_dummy.txt")
    
    # Update content to show button
    node.popup.update_content("Node", "File", node.watch_path, "Notes")
    node.popup.setVisible(True) # Make sure parent is visible so children are visible
    
    if not node.popup.btn_open.isVisible():
        print("FAIL: Open button should be visible")
        sys.exit(1)
    print("PASS: Open button visible")
    
    # We can't easily verify QDesktopServices won't open, but we can call the method
    # and ensure it doesn't crash.
    node.open_attachment()
    print("PASS: open_attachment called without error")
    
    # 3. Test Hover Timer Logic
    print("Testing Hover Timer...")
    if not node.hide_timer.isActive():
        # It shouldn't be active initially
        pass
    else:
        print("FAIL: Timer active initially")
        
    # Simulate Leave
    node.start_hide_timer()
    if not node.hide_timer.isActive():
        print("FAIL: Timer should be active after start_hide_timer")
        sys.exit(1)
    print("PASS: Timer started")
    
    # Simulate Enter Popup
    node.stop_hide_timer()
    if node.hide_timer.isActive():
        print("FAIL: Timer should be stopped")
        sys.exit(1)
    print("PASS: Timer stopped")

    # Cleanup
    if os.path.exists("test_dummy.txt"):
        os.remove("test_dummy.txt")

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_test()
