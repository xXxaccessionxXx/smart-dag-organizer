
import struct
import os

def generate_ico(filename):
    width = 64
    height = 64
    
    # 1. Generate BMP Data (DIB Header + Pixels)
    # DIB Header (40 bytes)
    # ICO BMP height is usually height * 2 (for mask), but modern ones can differ. 
    # Standard: height * 2. 
    # Let's use standard BMP structure but without the 14-byte file header.
    
    dib_header_size = 40
    # Width: 64, Height: 64*2 = 128 (for XOR and AND masks)
    # But for 32bpp usually we just use height and alpha channel.
    # Let's stick to simple 24bpp with no compression.
    
    # Total size of pixel data
    # Row size padded to 4 bytes. 64 * 3 = 192, divisible by 4.
    row_size = width * 3
    pixel_data_size = row_size * height
    
    # DIB Header
    # Height is doubled in ICO header for "true" ICOs usually, but let's try simple.
    # Actually, simplest is PNG inside ICO for modern Windows, but PyInstaller might need old style.
    # Let's do standard BMP style with explicit mask.
    
    # Mask: 1 bit per pixel, row padded to 32 bits (4 bytes).
    # 64 pixels -> 8 bytes. 8 bytes is multiple of 4.
    mask_row_size = 8
    mask_size = mask_row_size * height
    
    total_size = dib_header_size + pixel_data_size + mask_size
    
    # DIB Header
    # biHeight must be height * 2
    dib_header = struct.pack('<IiiHHIIIIII', 
        40, width, height * 2, 1, 24, 0, 0, 0, 0, 0, 0
    )
    
    # Pixel Data (Blue background with Cyan cross)
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            # BGR format (bottom-up usually? yes)
            # but let's just fill it.
            if abs(x - y) < 5 or abs(x - (height - y)) < 5:
                pixels.extend([255, 255, 0]) # Cyan
            else:
                pixels.extend([50, 20, 20]) # Dark Blue
    
    # Mask Data (0 = opaque, 1 = transparent)
    # All opaque
    mask = bytearray(mask_size) 
    
    bmp_data = dib_header + pixels + mask
    
    # 2. ICO Header
    # idReserved, idType=1(ICO), idCount=1
    ico_header = struct.pack('<HHI', 0, 1, 1)
    
    # 3. Directory Entry
    # bWidth, bHeight, bColorCount, bReserved, wPlanes, wBitCount, dwBytesInRes, dwImageOffset
    # Width 0 means 256. 64 is 64.
    dir_entry = struct.pack('<BBBBHHII', 
        width, height, 0, 0, 1, 24, len(bmp_data), 6 + 16
    )
    
    with open(filename, 'wb') as f:
        f.write(ico_header)
        f.write(dir_entry)
        f.write(bmp_data)
        
    print(f"Generated {filename}")

if __name__ == "__main__":
    try:
        generate_ico("icon.ico")
        with open("success.log", "w") as f:
            f.write("Success")
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(str(e))

