
import sys
import os
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from PyQt6.QtCore import QRectF

sys.path.append(os.getcwd())
app = QApplication(sys.argv)

from src.workflow_organizer import SmartNode, ConnectionLine

def run_debug():
    scene = QGraphicsScene()
    node_A = SmartNode("Node A", 0, 0, None)
    node_B = SmartNode("Node B", 300, 0, None)
    node_C = SmartNode("Node C", 600, 0, None)
    
    scene.addItem(node_A)
    scene.addItem(node_B)
    scene.addItem(node_C)

    line_AB = ConnectionLine(node_A, node_B)
    line_BC = ConnectionLine(node_B, node_C)
    
    scene.addItem(line_AB)
    scene.addItem(line_BC)
    
    node_A.connected_lines.append(line_AB)
    node_B.connected_lines.append(line_AB)
    node_B.connected_lines.append(line_BC)
    node_C.connected_lines.append(line_BC)

    print(f"Initial: A={node_A.isVisible()}, B={node_B.isVisible()}, C={node_C.isVisible()}")
    
    print("Collapsing A...")
    node_A.toggle_collapse()
    
    print(f"Post-Collapse A: A={node_A.isVisible()}, B={node_B.isVisible()}, C={node_C.isVisible()}")
    print(f"Line AB visible: {line_AB.isVisible()}")
    print(f"Line BC visible: {line_BC.isVisible()}")

    if not node_B.isVisible():
        print("PASS: Node B is hidden.")
    else:
        print("FAIL: Node B is visible.")
        
    if not node_C.isVisible():
        print("PASS: Node C is hidden.")
    else:
        print("FAIL: Node C is visible.")

if __name__ == "__main__":
    run_debug()
