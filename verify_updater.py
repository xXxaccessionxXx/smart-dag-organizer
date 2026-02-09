
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.updater import UpdateManager

class TestUpdater(unittest.TestCase):
    @patch('urllib.request.urlopen')
    def test_check_update_available(self, mock_urlopen):
        # Mock Response: Version 2.0.0
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"version": "2.0.0", "url": "http://test.com", "notes": "Major Update"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        updater = UpdateManager("http://dummy.url")
        has_update, ver, url, notes = updater.check_for_updates()
        
        print(f"\n[Test] Current: 1.0.0 | Remote: {ver} -> Update Available: {has_update}")
        
        self.assertTrue(has_update)
        self.assertEqual(ver, "2.0.0")
        self.assertEqual(url, "http://test.com")

    @patch('urllib.request.urlopen')
    def test_check_no_update(self, mock_urlopen):
        # Mock Response: Version 0.9.0
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"version": "0.9.0", "url": "", "notes": ""}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        updater = UpdateManager("http://dummy.url")
        has_update, ver, url, notes = updater.check_for_updates()
        
        print(f"[Test] Current: 1.0.0 | Remote: {ver} -> Update Available: {has_update}")
        
        self.assertFalse(has_update)

if __name__ == '__main__':
    unittest.main()
