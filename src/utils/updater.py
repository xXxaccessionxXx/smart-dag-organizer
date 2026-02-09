
import json
import urllib.request
from src.version import APP_VERSION

class UpdateManager:
    def __init__(self, version_url):
        self.version_url = version_url

    def check_for_updates(self):
        """
        Checks the remote URL for a version.json file.
        Returns: (has_update, new_version, download_url, release_notes)
        """
        try:
            with urllib.request.urlopen(self.version_url, timeout=5) as url:
                data = json.loads(url.read().decode())
                
                remote_version = data.get("version", "0.0.0")
                download_url = data.get("url", "")
                notes = data.get("notes", "")

                if self._parse_version(remote_version) > self._parse_version(APP_VERSION):
                    return True, remote_version, download_url, notes
                
        except Exception as e:
            print(f"[Update Check Failed] {e}")
            
        return False, None, None, None

    def _parse_version(self, v_str):
        try:
            return tuple(map(int, v_str.split(".")))
        except:
            return (0, 0, 0)
