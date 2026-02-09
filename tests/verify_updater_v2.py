
import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import tempfile
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.updater import UpdateManager

class TestUpdaterRestart(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.zip_path = os.path.join(self.test_dir, "update.zip")
        
        # Create a dummy zip file
        import zipfile
        with zipfile.ZipFile(self.zip_path, 'w') as zf:
            zf.writestr("SmartDAGOrganizer/test.txt", "New Version Content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('ctypes.windll.shell32.ShellExecuteW')
    @patch('sys.exit')
    @patch('subprocess.Popen') 
    def test_restart_and_install(self, mock_popen, mock_exit, mock_shell_execute):
        # Mock sys.argv and sys.executable
        with patch.object(sys, 'argv', ['/path/to/script.py']):
            with patch.object(sys, 'executable', '/path/to/python.exe'):
                
                manager = UpdateManager("http://mock_url")
                manager.download_path = self.zip_path
                
                # Run the method
                manager.restart_and_install()
                
                # Check if ShellExecute was called
                self.assertTrue(mock_shell_execute.called)
                args = mock_shell_execute.call_args[0]
                # args: (None, "runas", batch_script, params, None, show_cmd)
                
                self.assertEqual(args[1], "runas")
                batch_script_path = args[2]
                
                print(f"Verified ShellExecute called with script: {batch_script_path}")
                
                # Verify batch script content
                self.assertTrue(os.path.exists(batch_script_path))
                with open(batch_script_path, 'r') as f:
                    content = f.read()
                    print("\n--- Generated Batch Script ---")
                    print(content)
                    print("------------------------------\n")
                    
                    self.assertIn("tasklist /FI", content)
                    self.assertIn("xcopy", content)
                    self.assertIn("start \"\" \"\"/path/to/python.exe\"\" \"\"/path/to/script.py\"\"", content)
                    
                # Clean up batch script
                os.remove(batch_script_path)

if __name__ == '__main__':
    with open("verify_result.txt", "w") as f:
        try:
            # Create a test suite and run it
            suite = unittest.TestLoader().loadTestsFromTestCase(TestUpdaterRestart)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            if result.wasSuccessful():
                f.write("SUCCESS")
            else:
                f.write("FAILURE")
                for err in result.errors:
                    f.write(f"\nERROR: {err[1]}")
                for fail in result.failures:
                    f.write(f"\nFAIL: {fail[1]}")
        except Exception as e:
            f.write(f"EXCEPTION: {e}")
