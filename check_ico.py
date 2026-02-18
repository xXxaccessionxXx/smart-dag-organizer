
import struct
import os

def check_ico():
    path = "assets/icon.ico"
    if not os.path.exists(path):
        print("assets/icon.ico not found")
        return

    with open(path, "rb") as f:
        data = f.read()
    
    print(f"File size: {len(data)}")
    
    # Header
    reserved, type_, count = struct.unpack('<HHI', data[:6])
    print(f"Header: Reserved={reserved}, Type={type_}, Count={count}")
    
    # Entry
    entry_data = data[6:22]
    w, h, colors, res, planes, bpp, size, offset = struct.unpack('<BBBBHHII', entry_data)
    print(f"Entry: W={w}, H={h}, Colors={colors}, Res={res}, Planes={planes}, BPP={bpp}")
    print(f"       Size={size}, Offset={offset}")
    
    if offset + size > len(data):
        print("ERROR: Data extends past end of file")
    else:
        print("Data fits in file")
        
    # Check if data starts with PNG signature
    img_data = data[offset:offset+size]
    if img_data.startswith(b'\x89PNG\r\n\x1a\n'):
        print("Image data is valid PNG")
    else:
        print("Image data is NOT PNG")
        print(f"First 16 bytes: {img_data[:16]}")

if __name__ == "__main__":
    check_ico()
