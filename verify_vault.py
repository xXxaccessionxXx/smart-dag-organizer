
import sys
import os
import json
from src.utils.security import decrypt_credentials, get_cipher

def main():
    print("Verifying encryption...")
    enc_path = "assets/credentials.enc"
    
    if not os.path.exists(enc_path):
        print(f"Error: {enc_path} not found.")
        return

    try:
        # This will internally call get_cipher -> keyring.get_password
        data = decrypt_credentials(enc_path)
        
        if data and "installed" in data:
            print("[SUCCESS] Credentials successfully decrypted from Vault key!")
            print("Project ID:", data["installed"].get("project_id", "Unknown"))
        else:
            print("[ERROR] Decryption returned invalid data.")
            print(data)
            
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")

if __name__ == "__main__":
    main()
