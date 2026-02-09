
import sys
import os
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from PyQt6.QtCore import Qt, QPointF, QEvent
from PyQt6.QtGui import QMouseEvent

# Ensure src in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

app = QApplication(sys.argv)

def test_navigation():
    print("\n--- Testing Navigation Logic ---")
    try:
        from src.workflow_organizer import SmartView
        
        # Mock Window
        class MockWindow:
            theme_data = {"window_bg": "#000", "grid_light": "#111"}
            class MockConfig:
                def get_grid_style(self): return "Lines"
            config_manager = MockConfig()
            
        scene = QGraphicsScene(0, 0, 1000, 1000)
        view = SmartView(scene, MockWindow())
        view.resize(500, 500)
        view.show()
        
        # 1. Test Left Click Pan
        print("Testing Left Click Pan...")
        # Press
        press_event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(100, 100), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        view.mousePressEvent(press_event)
        
        if view._is_panning:
            print("PASS: Left Click started panning.")
        else:
            print("FAIL: Left Click did not start panning.")
            
        # Move
        move_event = QMouseEvent(QEvent.Type.MouseMove, QPointF(50, 50), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        view.mouseMoveEvent(move_event)
        
        # Check scrollbars (should have moved 50px)
        # Note: scrollbar value change logic is inverted (pulling scene)
        # delta = 50-100 = -50. value = value - (-50) = value + 50.
        # But wait, original value is 0. 
        # Let's just check if it changed.
        h_val = view.horizontalScrollBar().value()
        v_val = view.verticalScrollBar().value()
        print(f"Scroll values: {h_val}, {v_val}")
        
        # Release
        release_event = QMouseEvent(QEvent.Type.MouseButtonRelease, QPointF(50, 50), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        view.mouseReleaseEvent(release_event)
        
        if not view._is_panning:
             print("PASS: Left Click release stopped panning.")
        else:
             print("FAIL: Left Click release did not stop panning.")

        # 2. Test Right Click Selection
        print("Testing Right Click Selection...")
        # Reset DragMode
        view.setDragMode(QGraphicsView.DragMode.NoDrag)
        
        r_press = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(200, 200), Qt.MouseButton.RightButton, Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier)
        view.mousePressEvent(r_press)
        
        if view.dragMode() == QGraphicsView.DragMode.RubberBandDrag:
            print("PASS: Right Click enabled RubberBandDrag.")
        else:
            print(f"FAIL: Right Click did not enable RubberBandDrag. Mode: {view.dragMode()}")

    except Exception as e:
        print(f"CRITICAL TEST FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_navigation()
