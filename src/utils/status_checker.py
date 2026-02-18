import os
import time
from PyQt6.QtCore import QThread, pyqtSignal

class StatusChecker(QThread):
    results_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.paths_to_check = []
        self._running = True

    def set_paths(self, paths):
        """Update the list of paths to check."""
        self.paths_to_check = list(set(paths)) # Remove duplicates

    def stop(self):
        self._running = False
        self.wait()

    def run(self):
        while self._running:
            if not self.paths_to_check:
                time.sleep(1)
                continue

            results = {}
            # Check a batch of paths
            # We copy the list to avoid modification during iteration if set_paths is called
            current_paths = list(self.paths_to_check)
            
            for path in current_paths:
                if not self._running: break
                if not path: continue
                
                try:
                    exists = os.path.exists(path)
                    results[path] = exists
                except Exception:
                    results[path] = False
            
            if self._running and results:
                self.results_ready.emit(results)
            
            # Sleep a bit to avoid hammering the disk/cpu
            time.sleep(2.0) 
