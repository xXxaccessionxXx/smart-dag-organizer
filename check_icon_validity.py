
from PIL import Image
import os

icon_path = "assets/icon.ico"
try:
    if not os.path.exists(icon_path):
        print("Icon file missing.")
    else:
        img = Image.open(icon_path)
        print(f"Format: {img.format}")
        print(f"Size: {img.size}")
        print(f"Info: {img.info}")
        # standard ICO should have 'sizes' in info
        if 'sizes' in img.info:
            print(f"Sizes: {img.info['sizes']}")
        else:
            print("No multi-size info found.")
except Exception as e:
    with open("icon_validity_log.txt", "w") as f:
        f.write(f"Error checking icon: {e}\n")
else:
    with open("icon_validity_log.txt", "w") as f:
        f.write(f"Format: {img.format}\n")
        f.write(f"Size: {img.size}\n")
        f.write(f"Info: {img.info}\n")
        if 'sizes' in img.info:
            f.write(f"Sizes: {img.info['sizes']}\n")
        else:
            f.write("No multi-size info found.\n")
