
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from src.integrations.google_calendar import GoogleCalendarIntegration

class MockManager:
    def __init__(self):
        self.credentials_path = os.path.abspath("user_data/credentials.json") # Fake user path
        self.token_path = os.path.abspath("token.json")

def verify():
    manager = MockManager()
    integration = GoogleCalendarIntegration(manager)
    
    print("--- Verifying Credential Loading ---")
    
    # We want to test the logic inside get_service that finds the file
    # But get_service also does the OAuth flow which requires user interaction or existing token.
    # We just want to see WHICH file it picks.
    # We can inspect `integration.get_service` but it's hard without mocking `InstalledAppFlow`.
    
    # Instead, let's copy the logic we want to test or just check if the encrypted file mechanism works.
    # Actually, I can mock `InstalledAppFlow` to just print which file it was called with.
    
    import unittest.mock as mock
    
    with mock.patch('src.integrations.google_calendar.InstalledAppFlow') as MockFlow:
        # Mock run_local_server to return a fake creds object
        mock_creds = mock.Mock()
        mock_creds.valid = True
        mock_creds.to_json.return_value = "{}"
        
        MockFlow.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds
        
        # remove token.json if exists to force loading
        if os.path.exists(manager.token_path):
            os.remove(manager.token_path)
            
        try:
            integration.get_service()
        except Exception as e:
            print(f"Caught expected exception or error: {e}")
            
        # Check calls
        if MockFlow.from_client_secrets_file.called:
            args, _ = MockFlow.from_client_secrets_file.call_args
            print(f"InstalledAppFlow called with: {args[0]}")
            if "credentials.enc" in args[0] or ".json" in args[0]: # Temp file from enc ends in .json
                 # If it was a temp file from encryption, it's a random name but we can infer from context
                 pass
        else:
            print("InstalledAppFlow not called (maybe loaded from token?)")

if __name__ == "__main__":
    verify()
