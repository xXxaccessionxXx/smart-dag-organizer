
import sys
import os
from PyQt6.QtGui import QImage, QPainter, QColor, QBrush, QPen, QRadialGradient, QLinearGradient, QGuiApplication
from PyQt6.QtCore import Qt, QPoint, QPointF

# Ensure assets dir exists
if not os.path.exists("assets"):
    os.makedirs("assets")

def generate_icon():
    app = QGuiApplication(sys.argv)
    
    size = 512
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 1. Background (Rounded Square)
    rect = image.rect().adjusted(20, 20, -20, -20)
    bg_gradient = QLinearGradient(0, 0, size, size)
    bg_gradient.setColorAt(0, QColor("#1e1e1e"))
    bg_gradient.setColorAt(1, QColor("#121212"))
    
    painter.setBrush(QBrush(bg_gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(rect, 100, 100) # Soft corners
    
    # 2. Abstract Graph Structure
    # Center Point
    center = QPointF(size/2, size/2)
    
    # Nodes (Orbital)
    nodes = [
        (center + QPointF(0, -120), "#00f0ff"), # Top Cyan
        (center + QPointF(-100, 80), "#b829e0"), # Left Purple
        (center + QPointF(100, 80), "#00f0ff"),  # Right Cyan
    ]
    
    # Draw Lines first
    line_pen = QPen(QColor(100, 100, 100, 150))
    line_pen.setWidth(8)
    painter.setPen(line_pen)
    
    for p, color in nodes:
        painter.drawLine(center, p)
        
    painter.drawLine(nodes[0][0], nodes[1][0])
    painter.drawLine(nodes[1][0], nodes[2][0])
    painter.drawLine(nodes[2][0], nodes[0][0])
    
    # Draw Nodes
    def draw_node(pos, color_str, radius=35):
        # Glow
        glow = QRadialGradient(pos, radius * 2)
        glow.setColorAt(0, QColor(color_str))
        glow.setColorAt(1, Qt.GlobalColor.transparent)
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(pos, radius*2, radius*2)
        
        # Core
        painter.setBrush(QBrush(QColor("white")))
        painter.drawEllipse(pos, radius/2, radius/2)

    # Center Node (Primary)
    draw_node(center, "#b829e0", 50)
    
    # Peripheral Nodes
    for i, (p, c) in enumerate(nodes):
        draw_node(p, c, 35)

    painter.end()
    
    output_path = "assets/icon.png"
    image.save(output_path)
    print(f"Icon generated at: {output_path}")

if __name__ == "__main__":
    try:
        generate_icon()
    except Exception as e:
        print(f"Error generating icon: {e}")
        import traceback
        traceback.print_exc()
