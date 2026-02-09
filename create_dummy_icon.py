
import os

def create_valid_bmp(path):
    # Minimal 1x1 pixel BMP (White)
    # Header (14 bytes) + DIB Header (40 bytes) + Pixel Data (4 bytes) = 58 bytes
    bmp_data = (
        b'BM' + 
        b'\x3A\x00\x00\x00' + # File size (58 bytes)
        b'\x00\x00\x00\x00' + # Reserved
        b'\x36\x00\x00\x00' + # Offset to pixel data (54 bytes)
        b'\x28\x00\x00\x00' + # DIB Header Size (40 bytes)
        b'\x01\x00\x00\x00' + # Width (1)
        b'\x01\x00\x00\x00' + # Height (1)
        b'\x01\x00' +         # Planes (1)
        b'\x18\x00' +         # Bits per pixel (24)
        b'\x00\x00\x00\x00' + # Compression (0)
        b'\x04\x00\x00\x00' + # Image Size (4 bytes)
        b'\x00\x00\x00\x00' + # X pixels per meter
        b'\x00\x00\x00\x00' + # Y pixels per meter
        b'\x00\x00\x00\x00' + # Total colors
        b'\x00\x00\x00\x00' + # Important colors
        b'\xFF\xFF\xFF\x00'   # Pixel data (BGR: White) + Padding (255, 255, 255, 0)
    )
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    
    with open(path, 'wb') as f:
        f.write(bmp_data)
        
    print(f"Created valid BMP at: {os.path.abspath(path)}")

if __name__ == "__main__":
    create_valid_bmp("assets/icon.bmp")
