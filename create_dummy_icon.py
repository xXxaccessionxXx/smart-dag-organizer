
import os
import struct

def create_valid_ico(path):
    # Minimal 1x1 pixel BMP (White) for ICO
    # ICO Format:
    # Header (6 bytes)
    # Directory Entry (16 bytes)
    # BMP Data (40 bytes DIB Header + Pixel Data)
    
    # BMP DIB Header (40 bytes) + Pixel Data (4 bytes)
    # Note: For ICO, the BMP height must be doubled in the DIB header (2), 
    # but we are just embedding a simple PNG or raw BMP data usually.
    # Let's use a standard ICONDIRENTRY structure pointing to raw BMP data (excluding file header).
    
    # BMP Data (DIB Header + Pixels)
    # 40 bytes header + 4 bytes pixel data = 44 bytes
    bmp_header_size = 40
    width = 1
    height = 1 # In ICO this is seemingly doubled in height field of DIB? No, that's for AND mask.
    # Let's just make a simple uncompressed BMP data block.
    
    dib_header = (
        struct.pack('<I', 40) +        # Header Size
        struct.pack('<i', width) +     # Width
        struct.pack('<i', height * 2) + # Height (doubled for AND mask)
        struct.pack('<H', 1) +         # Planes
        struct.pack('<H', 24) +        # BPP
        struct.pack('<I', 0) +         # Compression
        struct.pack('<I', 0) +         # Image Size (0 for uncompressed)
        struct.pack('<i', 0) +         # X PPM
        struct.pack('<i', 0) +         # Y PPM
        struct.pack('<I', 0) +         # Colors
        struct.pack('<I', 0)           # Important Colors
    )
    
    # 1x1 Pixel (White) BGR
    pixel_data = b'\xFF\xFF\xFF'
    # Padding to 4 bytes boundary per row (1 pixel * 3 bytes = 3. Padding = 1 byte)
    pixel_padding = b'\x00'
    
    # XOR Mask (Color map)
    xor_mask = pixel_data + pixel_padding
    
    # AND Mask (Transparency) - 1 bit per pixel. 
    # 1 pixel = 1 bit. Padding to 32 bits (4 bytes).
    # 1 bit = 0 (Opaque).
    # Row padding: (1 * 1 + 31) // 32 * 4 = 4 bytes.
    and_mask = b'\x00\x00\x00\x00' 
    
    icon_image_data = dib_header + xor_mask + and_mask
    image_size = len(icon_image_data)
    
    # ICO Header
    ico_header = (
        struct.pack('<H', 0) + # Reserved
        struct.pack('<H', 1) + # Type (1 = Icon)
        struct.pack('<H', 1)   # Count (1 image)
    )
    
    # Directory Entry
    directory_entry = (
        struct.pack('B', width) +  # Width
        struct.pack('B', height) + # Height
        struct.pack('B', 0) +      # Colors (0 = >=8bpp)
        struct.pack('B', 0) +      # Reserved
        struct.pack('<H', 1) +     # Planes
        struct.pack('<H', 24) +    # BPP
        struct.pack('<I', image_size) +   # Size
        struct.pack('<I', 6 + 16)         # Offset (Header + Entry)
    )
    
    full_ico_data = ico_header + directory_entry + icon_image_data
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    
    with open(path, 'wb') as f:
        f.write(full_ico_data)
        
    print(f"Created valid ICO at: {os.path.abspath(path)}")

if __name__ == "__main__":
    create_valid_ico("assets/icon.ico")
