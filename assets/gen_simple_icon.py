
import struct

def generate_bmp(filename):
    width = 64
    height = 64
    
    # BMP Header
    file_size = 14 + 40 + (width * height * 3)
    header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
    
    # DIB Header
    dib_header = struct.pack('<IiiHHIIIIII', 40, width, height, 1, 24, 0, 0, 0, 0, 0, 0)
    
    # Pixel Data (Blue background with Cyan cross)
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            # BGR format
            if abs(x - y) < 5 or abs(x - (height - y)) < 5:
                # Cyan
                pixels.extend([255, 255, 0])
            else:
                # Dark Blue
                pixels.extend([50, 20, 20])
                
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(dib_header)
        f.write(pixels)
        
    print(f"Generated {filename}")

import os

if __name__ == "__main__":
    # Ensure correct path resolution relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "icon.bmp")
    
    generate_bmp(output_path)
    print(f"Icon generated at: {output_path}")
