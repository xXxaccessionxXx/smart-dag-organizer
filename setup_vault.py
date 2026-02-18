
import keyring
import secrets
from cryptography.fernet import Fernet
import sys

SERVICE_NAME = "SmartDAG_Organizer"
KEY_NAME = "encryption_key_v1"

def main():
    print("="*50)
    print("   Smart DAG - Vault Key Setup")
    print("="*50)
    
    # 1. Check if key already exists
    existing_key = keyring.get_password(SERVICE_NAME, KEY_NAME)
    
    if existing_key:
        print(f"[!] A key already exists in Windows Credential Manager for {SERVICE_NAME}/{KEY_NAME}.")
        response = input("Do you want to OVERWRITE it with a new key? (y/N): ").strip().lower()
        if response != 'y':
            print("Operation cancelled. Existing key preserved.")
            return

    # 2. Generate new key
    print("Generating new Fernet key...")
    new_key = Fernet.generate_key().decode('utf-8')
    
    # 3. Store in Vault
    print("Storing key in Windows Vault...")
    try:
        keyring.set_password(SERVICE_NAME, KEY_NAME, new_key)
        print("[SUCCESS] Key successfully stored in Windows Credential Manager.")
        print(f"Service: {SERVICE_NAME}")
        print(f"Account: {KEY_NAME}")
    except Exception as e:
        print(f"[ERROR] Failed to store key: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
