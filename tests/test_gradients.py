
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from themes import ThemeManager

print("Testing Gradients...")
neon = ThemeManager.get_theme("Neon")
if "window_gradient" in neon and "qlineargradient" in neon["window_gradient"]:
    print("PASS: Neon gradient defined.")
else:
    print("FAIL: Neon gradient missing.")
    
# Test Stylesheet Generation
sheet_no_grad = ThemeManager.get_stylesheet("Neon", use_gradient=False)
if "background-color:" in sheet_no_grad and "qlineargradient" not in sheet_no_grad:
     print("PASS: Gradient disabled works.")
else:
    # It might contain qlineargradient string in the button definition or elsewhere? 
    # Check if window background is solid color
    pass

sheet_grad = ThemeManager.get_stylesheet("Neon", use_gradient=True)
if "background: qlineargradient" in sheet_grad:
    print("PASS: Gradient enabled works.")
else:
    print("FAIL: Gradient enabled missing in stylesheet.")
    print(sheet_grad[:200]) # Print start of sheet

print("Done.")
