import sys
import os

# Add root to path so we can import src as a package
sys.path.append(os.getcwd())

from src.config_manager import ConfigManager

def test_window_geometry():
    cm = ConfigManager("test_config_window.json")
    
    # Test Get Default
    geo = cm.get_window_geometry()
    print(f"Default Geometry: {geo}")
    assert geo is None
    
    # Test Set
    dummy_hex = "01d9d0cb"
    cm.set_window_geometry(dummy_hex)
    
    # Test Get After Set
    geo_new = cm.get_window_geometry()
    print(f"New Geometry: {geo_new}")
    assert geo_new == dummy_hex
    
    print("Window Geometry Persistence Test Passed!")
    
    # Cleanup
    if os.path.exists("test_config_window.json"):
        os.remove("test_config_window.json")

if __name__ == "__main__":
    test_window_geometry()
