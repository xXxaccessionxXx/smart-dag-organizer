
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
        Creates a batch script to replace files and restart the application,
        handling UAC elevation if necessary.
        """
        try:
            exe_path = sys.executable
            app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            
            # If frozen (exe), app_dir is the dir containing the exe
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(exe_path)
            
            # Extract to temp
            extract_dir = os.path.join(tempfile.gettempdir(), "SmartDAG_Update_Extracted")
            if os.path.exists(extract_dir):
                import shutil
                shutil.rmtree(extract_dir)
            
            print(f"Extracting update to {extract_dir}...")
            with zipfile.ZipFile(self.download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            # Locate source content
            source_dir = extract_dir
            if os.path.exists(os.path.join(extract_dir, "SmartDAGOrganizer")):
                source_dir = os.path.join(extract_dir, "SmartDAGOrganizer")
            
            # Create Batch Script
            batch_script = os.path.join(tempfile.gettempdir(), "update_installer.bat")
            
            # Determine launch command
            if getattr(sys, 'frozen', False):
                launch_cmd = f'""{exe_path}""' # Double quotes for batch
            else:
                script_path = os.path.abspath(sys.argv[0])
                launch_cmd = f'""{exe_path}"" ""{script_path}""'
            
            # Batch Content
            # 1. Wait for PID (we pass PID to script)
            # 2. XCOPY
            # 3. Relaunch
            
            # We use a loop to wait for the file to be writable (app closed)
            batch_content = f"""
@echo off
title Updating Smart DAG Organizer...
echo Waiting for application to close...

:WAIT_LOOP
timeout /t 1 /nobreak > NUL
tasklist /FI "PID eq {os.getpid()}" 2>NUL | find /I /N "{os.getpid()}" >NUL
if "%ERRORLEVEL%"=="0" goto WAIT_LOOP

echo Updating files...
xcopy "{source_dir}" "{app_dir}" /E /Y /I /Q

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to copy files. Please run as Administrator.
    pause
    exit /b %ERRORLEVEL%
)

echo Update complete.
echo Restarting application...
start "" {launch_cmd}

echo Cleaning up...
del "{self.download_path}"
(goto) 2>nul & del "%~f0"
"""
            
            with open(batch_script, "w") as f:
                f.write(batch_content)
                
            print(f"Update script created at {batch_script}")
            
            # Execute with ShellExecute to allow UAC elevation if needed
            # We use "runas" verb if we suspect we need admin, or just always try to elevate if purely replacing?
            # Actually, standard user might not need elevation if installed in AppData.
            # But prompt says "requires me to install portable file", implying failure.
            # Let's try to run it. If it fails, the batch script pauses (in my code below I removed pause but adding it back might be good for debugging, but we want auto).
            
            # Better approach: Use ShellExecute to run the batch script.
            # On Windows, .bat files need 'cmd /c' or just shell=True.
            
            import ctypes
            from ctypes import wintypes
            
            # We will use ShellExecuteW to run the batch file.
            # passing "runas" triggers UAC prompt if needed, or if the user settings require it.
            # However, for simply running a batch in temp, we don't strictly need runas UNLESS the xcopy target is protected.
            # It's safer to request elevation for the update script to ensure xcopy works on Program Files.
            
            params = ""
            show_cmd = 1 # SW_SHOWNORMAL
            
            # If we are not admin, and we might need it (we don't check strict permissions here to keep it simple, 
            # but xcopy to Program Files DEFINITELY needs it).
            # Let's execute with 'runas' to be safe for the updater.
            
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                batch_script, 
                params, 
                None, 
                show_cmd
            )
            
            if ret <= 32:
                # Error happened (ret <= 32 is error)
                # But if user declined UAC, it might be one of these.
                print(f"ShellExecute failed with code {ret}")
                pass
            
            sys.exit(0)
            
        except Exception as e:
            print(f"[Install Failed] {e}")
            return False

    def _parse_version(self, v_str):
        try:
            return tuple(map(int, v_str.split(".")))
        except:
            return (0, 0, 0)
