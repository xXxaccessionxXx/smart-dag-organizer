
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from src.themes import ThemeManager

print("Testing Theme Retrieval...")
dark = ThemeManager.get_theme("Dark")
if dark["window_bg"] == "#1e1e1e":
    print("PASS: Dark Theme OK")
else:
    print("FAIL: Dark Theme Incorrect")

light = ThemeManager.get_theme("Light")
if light["window_bg"] == "#f3f3f3":
    print("PASS: Light Theme OK")
else:
    print("FAIL: Light Theme Incorrect")

print("Testing Stylesheet Generation...")
sheet = ThemeManager.get_stylesheet("Neon")
if "background-color: #0a0a12" in sheet:
    print("PASS: Neon Stylesheet Generated")
else:
    print("FAIL: Neon Stylesheet Logic Error")
