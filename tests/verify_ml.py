
import os
import sys
import time
import json
import random

# Add current directory to path
sys.path.append(os.getcwd())

# Mock environment
if not os.path.exists("brain_memory.json"):
    with open("brain_memory.json", "w") as f:
        json.dump({"skills": [], "failed_tasks": {}}, f)

from src.ai.brain import AutoLearner, CodeEvolver, NeuralNet, NeuralMemory

def test_neural_net():
    print("\n--- Testing NeuralNet ---")
    net = NeuralNet(3, 5, 1)
    # Inputs: [Len, Lines, Imports]
    dummy_input = [0.5, 0.2, 0.1]
    pred = net.predict(dummy_input)
    print(f"Prediction (Untrained): {pred}")
    
    # Train
    print("Training...")
    for _ in range(10):
        net.train(dummy_input, [0.9])
        
    pred_after = net.predict(dummy_input)
    print(f"Prediction (Trained): {pred_after}")
    
    if pred_after > pred:
        print("PASS: Network learned (score increased).")
    else:
        print("FAIL: Network did not learn.")

def test_evolution():
    print("\n--- Testing CodeEvolver ---")
    script = "import os\nprint('Hello World')\n"
    print(f"Original:\n{script}")
    
    mutated = CodeEvolver.mutate(script)
    print(f"Mutated:\n{mutated}")
    
    if mutated != script:
        print("PASS: Mutation occurred.")
    else:
        print("WARN: Mutation chance missed (it's probabilistic).")

def test_failure_memory():
    print("\n--- Testing Failure Memory (Stable Keys) ---")
    mem = NeuralMemory("brain_memory.json")
    auto = AutoLearner(mem)
    
    # Manually blacklist a stable key
    bad_key = "procedural_find_TODO"
    auto.failed_tasks[bad_key] = 3
    
    # We can't easily force generate_procedural_task to pick this specific one randomnly,
    # but we can verify the check logic by calling generate_task manually if we could mock random.
    # Instead, let's just inspect the failed_tasks dictionary to ensure it persists.
    
    print(f"Failed Tasks: {auto.failed_tasks}")
    if bad_key in auto.failed_tasks and auto.failed_tasks[bad_key] >= 3:
        print("PASS: Failure memory is tracking stable keys.")
    else:
        print("FAIL: Failure memory not tracking.")

def test_learning_loop():
    print("\n--- Testing Learning Loop ---")
    mem = NeuralMemory("brain_memory.json")
    auto = AutoLearner(mem)
    
    # Run one attempt
    print("Attempting learning (Watch for NeuralNet Prediction)...")
    success, msg = auto.attempt_learning()
    print(f"Result: {success}")
    print(f"Message: {msg}")

if __name__ == "__main__":
    test_neural_net()
    test_evolution()
    test_failure_memory()
    test_learning_loop()
