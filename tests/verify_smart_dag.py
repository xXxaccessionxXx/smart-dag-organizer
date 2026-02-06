
import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from PyQt6.QtCore import QRectF

# Ensure src is in path
sys.path.append(os.getcwd())

# We need a QApplication for QGraphicsItems
app = QApplication(sys.argv)

from src.workflow_organizer import SmartNode, ConnectionLine

class TestSmartDAG(unittest.TestCase):
    def setUp(self):
        self.scene = QGraphicsScene()
        # Mocking main window ref as None for basic tests
        self.node_A = SmartNode("Node A", 0, 0, None)
        self.node_B = SmartNode("Node B", 300, 0, None)
        self.node_C = SmartNode("Node C", 600, 0, None)
        
        self.scene.addItem(self.node_A)
        self.scene.addItem(self.node_B)
        self.scene.addItem(self.node_C)

        # Connect A -> B -> C
        self.line_AB = ConnectionLine(self.node_A, self.node_B)
        self.line_BC = ConnectionLine(self.node_B, self.node_C)
        
        self.scene.addItem(self.line_AB)
        self.scene.addItem(self.line_BC)
        
        # Link in nodes (mimicking main window logic)
        self.node_A.connected_lines.append(self.line_AB)
        self.node_B.connected_lines.append(self.line_AB) # End of AB
        self.node_B.connected_lines.append(self.line_BC) # Start of BC
        self.node_C.connected_lines.append(self.line_BC)

    def test_recursive_collapse(self):
        # Initial: All visible
        print(f"Initial: A={self.node_A.isVisible()}, B={self.node_B.isVisible()}, C={self.node_C.isVisible()}")
        self.assertTrue(self.node_A.isVisible())
        self.assertTrue(self.node_B.isVisible())
        self.assertTrue(self.node_C.isVisible())
        
        # Test Collapse Button
        self.assertEqual(self.node_A.collapse_btn.toPlainText(), "[-]")
        
        # Collapse A -> Should hide B and C
        print("Collapsing A...")
        self.node_A.toggle_collapse()
        print(f"After Collapse A: A={self.node_A.isVisible()}, B={self.node_B.isVisible()}, C={self.node_C.isVisible()}")
        self.assertTrue(self.node_A.is_collapsed)
        
        # Check Button Text Update
        self.assertEqual(self.node_A.collapse_btn.toPlainText(), "[+]")

        # Check NO Resizing (Req: do not shrink)
        # Should remain default size (200x80)
        self.assertEqual(self.node_A.rect().height(), 80, "Node height should stay 80 when collapsed")
        
        # NOTE: In our logic, line.end_node gets hidden.
        # Check Lines
        self.assertFalse(self.line_AB.isVisible(), "Line AB should be hidden")
        
        # Check Nodes
        self.assertFalse(self.node_B.isVisible(), "Node B should be hidden") 
        self.assertFalse(self.node_C.isVisible(), "Node C should be hidden")

        # Expand A -> Should show B and C
        print("Expanding A...")
        self.node_A.toggle_collapse()
        print(f"After Expand A: A={self.node_A.isVisible()}, B={self.node_B.isVisible()}, C={self.node_C.isVisible()}")
        self.assertEqual(self.node_A.collapse_btn.toPlainText(), "[-]")
        self.assertTrue(self.node_B.isVisible())
        self.assertTrue(self.node_C.isVisible())

    def test_rich_tooltip(self):
        self.node_A.notes = "Sample Notes"
        self.node_A.check_status()
        tooltip = self.node_A.toolTip()
        
        # Check for content presence rather than exact HTML tag structure
        self.assertIn("Node A", tooltip)
        self.assertIn("Sample Notes", tooltip)

        # Mock image attachment
        self.node_A.watch_path = "C:/test/image.png"
        self.node_A.attachment_type = "File"
        self.node_A.check_status()
        tooltip = self.node_A.toolTip()
        
        self.assertIn("<img src=", tooltip)
        self.assertIn("image.png", tooltip)

if __name__ == '__main__':
    unittest.main()
