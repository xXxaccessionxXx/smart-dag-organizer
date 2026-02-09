
import sys
import os
from PyQt6.QtWidgets import QApplication

# Adjust path
sys.path.append(os.getcwd())

from src.workflow_organizer import SmartWorkflowOrganizer, SmartNode, SmartLine

def verify():
    app = QApplication(sys.argv)
    window = SmartWorkflowOrganizer()
    
    # Create Nodes
    node_a = SmartNode("Parent", 0, 0, window)
    node_b = SmartNode("Child", 100, 100, window)
    window.scene.addItem(node_a)
    window.scene.addItem(node_b)
    window.nodes.extend([node_a, node_b])
    
    # Test auto_connect return
    line = window.auto_connect_nodes(node_a, node_b)
    if line and isinstance(line, SmartLine):
        print("PASS: auto_connect_nodes returns SmartLine")
    else:
        print("FAIL: auto_connect_nodes did not return SmartLine")
        
    # Test Animation Methods existence
    if hasattr(node_a, "animate_node_appearance"):
        print("PASS: animate_node_appearance exists")
    else:
        print("FAIL: animate_node_appearance missing")

    print("Verification execution finished.")

if __name__ == "__main__":
    verify()
