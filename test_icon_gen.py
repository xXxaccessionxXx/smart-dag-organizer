
import os
import struct
import subprocess
import shutil
import base64

def generate_ico(filename):
    with open("debug_log.txt", "a") as log:
        log.write(f"[Icon] Generating icon to {filename}...\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    original_png = os.path.join(base_dir, "assets", "acyclic.PNG")
    target_size = 256
    resized_png = os.path.join(base_dir, "assets", f"icon_{target_size}.png")
    final_ico = os.path.join(base_dir, "assets", "icon_final.ico")

    if os.path.exists(resized_png):
        try: os.remove(resized_png)
        except: pass

    if os.path.exists(original_png):
        with open("debug_log.txt", "a") as log:
            log.write(f"[Icon] Resizing {original_png}...\n")
        
        ps_script = (
            f"$path = '{original_png}'; "
            f"$out = '{resized_png}'; "
            "Add-Type -AssemblyName System.Drawing; "
            "$img = [System.Drawing.Image]::FromFile($path); "
            f"$new = new-object System.Drawing.Bitmap({target_size},{target_size}); "
            "$g = [System.Drawing.Graphics]::FromImage($new); "
            "$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic; "
            f"$g.DrawImage($img, 0, 0, {target_size}, {target_size}); "
            "$new.Save($out, [System.Drawing.Imaging.ImageFormat]::Png); "
            "$img.Dispose(); $new.Dispose(); $g.Dispose();"
        )
        cmd = ["powershell", "-noprofile", "-command", ps_script]
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with open("debug_log.txt", "a") as log:
                log.write("[Icon] PowerShell executed.\n")
        except Exception as e:
            with open("debug_log.txt", "a") as log:
                log.write(f"[Icon] PowerShell failed: {e}\n")

    source_png = resized_png if os.path.exists(resized_png) else original_png
    with open("debug_log.txt", "a") as log:
        log.write(f"[Icon] Using source: {source_png}\n")

    if os.path.exists(source_png):
        try:
            with open(source_png, "rb") as f:
                png_data = f.read()
            
            ico_header = struct.pack('<HHI', 0, 1, 1)
            w_byte = 0
            h_byte = 0
            bpp = 32
            img_size = len(png_data)
            offset = 6 + 16
            
            dir_entry = struct.pack('<BBBBHHII', 
                w_byte, h_byte, 0, 0, 1, bpp, img_size, offset
            )
            
            with open(final_ico, 'wb') as f:
                f.write(ico_header)
                f.write(dir_entry)
                f.write(png_data)
                
            with open("debug_log.txt", "a") as log:
                log.write(f"[Icon] Created {final_ico}, Size: {len(png_data)+22}\n")
            
            if filename != final_ico:
                 shutil.copy2(final_ico, filename)

        except Exception as e:
            with open("debug_log.txt", "a") as log:
                log.write(f"[Icon] Failed to create ICO: {e}\n")

if __name__ == "__main__":
    generate_ico("assets/icon_final.ico")
