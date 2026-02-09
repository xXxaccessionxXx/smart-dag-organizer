import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add root to path
sys.path.append(os.getcwd())

try:
    from src.utils.updater import UpdateManager
    from src.launcher import GenesisLauncher
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

class TestUpdater(unittest.TestCase):
    def test_instantiation(self):
        um = UpdateManager("http://example.com/version.json")
        self.assertIsNotNone(um)
        print("UpdateManager instantiated successfully.")
        
    @patch('src.utils.updater.urllib.request.urlopen')
    def test_check_update_no_update(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"version": "0.0.0", "url": "http://test", "notes": "none"}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        um = UpdateManager("http://test")
        has_update, _, _, _ = um.check_for_updates()
        self.assertFalse(has_update)
        print("Check update (no update) passed.")

if __name__ == "__main__":
    unittest.main()
