import sys
import os
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def update_icons():
    # App needed for QImage handling in some contexts/plugins
    # app = QApplication(sys.argv)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(base_dir, "acyclic.PNG")
    
    if not os.path.exists(source_path):
        print(f"Error: {source_path} not found.")
        return

    # Load Source
    image = QImage(source_path)
    if image.isNull():
        print("Failed to load image.")
        return

    print(f"Loaded {source_path} ({image.width()}x{image.height()})")

    # 1. Save as icon.png (Standard)
    target_png = os.path.join(base_dir, "icon.png")
    image.save(target_png)
    print(f"Generated {target_png}")

    # 2. Save as icon.bmp
    target_bmp = os.path.join(base_dir, "icon.bmp")
    image.save(target_bmp)
    print(f"Generated {target_bmp}")

    # 3. Save as icon.ico
    # We resize to common icon sizes? 
    # For now, just saving the image as ICO. 
    # If the user has Pillow, we could do better, but this handles basic needs.
    target_ico = os.path.join(base_dir, "icon.ico")
    
    # Resize to 256x256 if larger, as some Windows versions struggle with massive icons
    if image.width() > 256 or image.height() > 256:
         scaled = image.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
         scaled.save(target_ico, "ICO")
    else:
         image.save(target_ico, "ICO")
         
    print(f"Generated {target_ico}")

if __name__ == "__main__":
    update_icons()
