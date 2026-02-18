
import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

from src.utils.security import encrypt_data_to_file

def main():
    input_path = "assets/credentials.json"
    output_path = "assets/credentials.enc"
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
        
    print(f"Reading {input_path}...")
    with open(input_path, 'r') as f:
        data = f.read()
        
    print(f"Encrypting to {output_path}...")
    success = encrypt_data_to_file(data, output_path)
    
    if success:
        print("Success! You can now safely commit 'assets/credentials.enc'.")
        print("Make sure 'assets/credentials.json' is still in .gitignore.")
    else:
        print("Encryption failed.")

if __name__ == "__main__":
    main()
