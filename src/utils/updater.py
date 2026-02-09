
import json
import urllib.request
import os
import sys
import zipfile
import subprocess
import tempfile
import time
from src.version import APP_VERSION

class UpdateManager:
    def __init__(self, version_url):
        self.version_url = version_url
        self.download_path = os.path.join(tempfile.gettempdir(), "SmartDAG_Update.zip")

    def check_for_updates(self):
        """
        Checks the remote URL for a version.json file.
        Returns: (has_update, new_version, download_url, release_notes)
        """
        try:
            print(f"Checking for updates from: {self.version_url}")
            # simple header to avoid some 403s
            req = urllib.request.Request(self.version_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=5) as url:
                data = json.loads(url.read().decode())
                
                remote_version = data.get("version", "0.0.0")
                download_url = data.get("url", "")
                notes = data.get("notes", "")
                
                print(f"Local: {APP_VERSION}, Remote: {remote_version}")

                if self._parse_version(remote_version) > self._parse_version(APP_VERSION):
                    return True, remote_version, download_url, notes
                
        except Exception as e:
            print(f"[Update Check Failed] {e}")
            
        return False, None, None, None

    def download_update(self, url, progress_callback=None):
        """
        Downloads the update zip file from the given URL.
        progress_callback: function(int) -> None (0-100)
        """
        try:
            print(f"Downloading update from {url}...")
            def _report(block_num, block_size, total_size):
                if total_size > 0 and progress_callback:
                    percent = int((block_num * block_size * 100) / total_size)
                    progress_callback(percent)

            urllib.request.urlretrieve(url, self.download_path, _report)
            print("Download complete.")
            return True
        except Exception as e:
            print(f"[Download Failed] {e}")
            return False

    def restart_and_install(self):
        """
        Creates a batch script to replace files and restart the application.
        """
        try:
            exe_path = sys.executable
            app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            
            # If running from source (python.exe), app_dir is the script dir
            # If frozen (exe), app_dir is the dir containing the exe
            
            # We need to extract the zip to a temporary folder
            extract_dir = os.path.join(tempfile.gettempdir(), "SmartDAG_Update_Extracted")
            if os.path.exists(extract_dir):
                import shutil
                shutil.rmtree(extract_dir)
            
            print(f"Extracting update to {extract_dir}...")
            with zipfile.ZipFile(self.download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            # Locate the inner folder if it exists (SmartDAGOrganizer/...)
            # The portable zip usually has a root folder "SmartDAGOrganizer"
            source_dir = extract_dir
            if os.path.exists(os.path.join(extract_dir, "SmartDAGOrganizer")):
                source_dir = os.path.join(extract_dir, "SmartDAGOrganizer")
            
            # Create Batch Script
            batch_script = os.path.join(tempfile.gettempdir(), "update_installer.bat")
            
            # Check if we are running as a frozen exe or python script
            is_frozen = getattr(sys, 'frozen', False)
            
            launch_cmd = f'"{exe_path}"'
            if not is_frozen:
                # If python script, we need to relaunch the script
                # Assuming main.py or launcher.py is the entry point
                script_path = os.path.abspath(sys.argv[0])
                launch_cmd = f'"{exe_path}" "{script_path}"'
            
            # Batch contents:
            # 1. Wait for PID to close
            # 2. XCOPY /E /Y /I source_dir destination_dir
            # 3. Start application
            # 4. Delete temp files
            
            # Using timeout /t 2 to give app time to close
            
            batch_content = f"""
@echo off
title Updating Smart DAG Organizer...
echo Waiting for application to close...
timeout /t 3 /nobreak > NUL

echo Updating files from {source_dir} to {app_dir}...
xcopy "{source_dir}" "{app_dir}" /E /Y /I /Q

echo Update complete. Restarting...
start "" {launch_cmd}

echo Cleaning up...
del "{self.download_path}"
del "{batch_script}"
exit
            """
            
            with open(batch_script, "w") as f:
                f.write(batch_content)
                
            print(f"Update script created at {batch_script}")
            print("Launching update script and exiting...")
            
            subprocess.Popen([batch_script], shell=True)
            sys.exit(0)
            
        except Exception as e:
            print(f"[Install Failed] {e}")
            return False

    def _parse_version(self, v_str):
        try:
            return tuple(map(int, v_str.split(".")))
        except:
            return (0, 0, 0)
