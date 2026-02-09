
import sys
import os
import ctypes

print("Python Executable:", sys.executable)
try:
    print("ctypes.windll:", ctypes.windll)
    print("ShellExecuteW:", ctypes.windll.shell32.ShellExecuteW)
except Exception as e:
    print("Error accessing ctypes:", e)

class Mock:
    pass

sys.modules['src'] = Mock() # mocking src to avoid import errors if needed?
# actually we need real src.utils.updater

try:
    sys.path.append(os.getcwd())
    from src.utils.updater import UpdateManager
    print("UpdateManager imported successfully")
except ImportError as e:
    print("ImportError:", e)
