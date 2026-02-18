import os
import sys

def check_png():
    print(f"CWD: {os.getcwd()}")
    png_path = "assets/acyclic.PNG"
    abs_path = os.path.abspath(png_path)
    print(f"Checking: {abs_path}")
    
    if os.path.exists(png_path):
        print("File exists.")
        try:
            with open(png_path, "rb") as f:
                header = f.read(16)
            print(f"Header: {header}")
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                print("Valid PNG signature.")
            else:
                print("Invalid PNG signature.")
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("File not found.")
        # List dir content
        print(f"Dir content of assets: {os.listdir('assets')}")

if __name__ == "__main__":
    check_png()
