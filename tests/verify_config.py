
import sys
import os
sys.path.append(os.getcwd())
from src.config_manager import ConfigManager

def test_config():
    print("Testing ConfigManager...")
    
    # 1. Read initial state
    initial_state = ConfigManager.is_ai_enabled()
    print(f"Initial State: {initial_state}")
    
    # 2. Toggle
    state_1 = not initial_state
    ConfigManager.set_ai_enabled(state_1)
    print(f"Set to: {state_1}")
    
    # 3. Read back
    read_back_1 = ConfigManager.is_ai_enabled()
    print(f"Read Back: {read_back_1}")
    assert read_back_1 == state_1
    
    # 4. Toggle back (cleanup)
    ConfigManager.set_ai_enabled(initial_state)
    print(f"Restored to: {initial_state}")
    
    final_read = ConfigManager.is_ai_enabled()
    assert final_read == initial_state
    
    print("ConfigManager verification successful.")

if __name__ == "__main__":
    test_config()
