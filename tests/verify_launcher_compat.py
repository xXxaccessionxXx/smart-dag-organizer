
import sys
import os

sys.path.append(os.getcwd())

from src.config_manager import ConfigManager

def run_test():
    print("Testing ConfigManager Compatibility...")
    
    try:
        # Test 1: Static Method Access
        enabled = ConfigManager.is_ai_enabled()
        print(f"PASS: is_ai_enabled() returned {enabled}")
        
        # Test 2: Setter
        ConfigManager.set_ai_enabled(False)
        if ConfigManager.is_ai_enabled() is not False:
            print("FAIL: set_ai_enabled(False) did not persist")
            sys.exit(1)
        print("PASS: set_ai_enabled(False) worked")
        
        # Restore
        ConfigManager.set_ai_enabled(True)
        print("PASS: set_ai_enabled(True) worked")
        
    except AttributeError as e:
        print(f"FAIL: AttributeError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: Unexpected Error: {e}")
        sys.exit(1)

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_test()
