import sys
import os

# Add 'src' to the python path so imports find the modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from src.launcher import GenesisLauncher
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GenesisLauncher()
    window.show()
    sys.exit(app.exec())
