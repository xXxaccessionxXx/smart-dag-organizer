
import os
import sys

icon_path = "assets/icon.ico"
if os.path.exists(icon_path):
    print(f"Opening {icon_path}...")
    try:
        os.startfile(icon_path)
    except Exception as e:
        print(f"Error opening icon: {e}")
else:
    print(f"Icon not found: {icon_path}")
