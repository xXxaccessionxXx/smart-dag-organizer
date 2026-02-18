
import struct
import os

def analyze_ico(filename):
    if not os.path.exists(filename):
        print(f"Error: {filename} does not exist.")
        return

    size = os.path.getsize(filename)
    print(f"File: {filename}, Size: {size} bytes")

    with open(filename, "rb") as f:
        header = f.read(6)
        if len(header) < 6:
            print("Invalid header length")
            return
            
        reserved, type_val, count = struct.unpack('<HHI', header)
        print(f"Header: Reserved={reserved}, Type={type_val} (1=Icon), Count={count} images")
        
        if type_val != 1:
            print("Error: Not an ICON file (Type != 1)")
            return

        for i in range(count):
            entry = f.read(16)
            if len(entry) < 16:
                break
            w, h, colors, res, planes, bpp, size, offset = struct.unpack('<BBBBHHII', entry)
            print(f"  Image #{i+1}: {w}x{h}, {bpp} bits, Size: {size}, Offset: {offset}")

try:
    import PIL
    print(f"Pillow Version: {PIL.__version__}")
except ImportError:
    print("Pillow NOT installed.")

analyze_ico("assets/icon.ico")
