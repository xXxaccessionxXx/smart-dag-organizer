import os
import sys

# Add current directory to path just in case
sys.path.append(os.getcwd())

try:
    from src.ai.brain import NeuralBrain, EnvironmentScanner
    
    print("Initializing Brain...")
    brain = NeuralBrain()
    
    print("Testing Environment Scanner...")
    files = EnvironmentScanner.scan(".")
    print(f"Files found: {files}")
    
    if not files:
        print("ERROR: No files found!")
        sys.exit(1)
        
    print("Updating Memory...")
    brain.memory.update_files(files)
    
    print("Testing Autonomous Coding...")
    # Simulate user input
    response = brain.get_response("Create a tool named my_timer that waits for 2 seconds")
    print(f"AI Response:\n{response}")
    
    # Check if script saved
    import json
    if os.path.exists("data/genesis_scripts.json"):
        with open("data/genesis_scripts.json", "r") as f:
            try:
                data = json.load(f)
                print(f"DEBUG: Keys in genesis_scripts.json: {list(data.keys())}")
                if "my_timer" in data:
                    print("SUCCESS: 'my_timer' found in genesis_scripts.json")
                    print("Content prefix:", data["my_timer"]["content"][:50])
                else:
                    print(f"FAILURE: 'my_timer' not found in {list(data.keys())}")
                    sys.exit(1)
            except json.JSONDecodeError:
                print("FAILURE: genesis_scripts.json is invalid JSON.")
                sys.exit(1)
    else:
        print("FAILURE: data/genesis_scripts.json does not exist.")
        sys.exit(1)
            
    print("Verification Successful.")
except Exception as e:
    print(f"Verification Failed: {e}")
    sys.exit(1)
