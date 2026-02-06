
import os
import sys
import json
import time

# Add current directory to path
sys.path.append(os.getcwd())

# Mock Environment
if not os.path.exists("brain_memory.json"):
    with open("brain_memory.json", "w") as f:
        json.dump({"skills": [], "failed_tasks": {}, "networks": {}}, f)

from src.ai.brain import AutoLearner, NeuralMemory, MetaClassifier, KnowledgeSeeker

def test_meta_classifier():
    print("\n--- Testing Meta-Classifier ---")
    mem = NeuralMemory("brain_memory.json")
    classifier = MetaClassifier(mem)
    
    tasks = [
        ("find TODO in project", "SKILL"),
        ("research the bible and god", "KNOWLEDGE"),
        ("analyze code complexity", "SKILL"),
        ("learn about divine truth", "KNOWLEDGE")
    ]
    
    for desc, expected in tasks:
        result = classifier.classify(desc)
        print(f"Task: '{desc}' -> {result} (Expected: {expected})")
        if result == expected:
            print("PASS")
        else:
            print("FAIL")

def test_knowledge_embedding():
    print("\n--- Testing Knowledge Embedding ---")
    mem = NeuralMemory("brain_memory.json")
    
    # Ensure bible.txt exists
    if not os.path.exists("knowledge/bible.txt"):
        os.makedirs("knowledge", exist_ok=True)
        with open("knowledge/bible.txt", "w") as f:
            f.write("In the beginning God created the heaven and the earth.\nAnd the earth was without form, and void.")
            
    msg = KnowledgeSeeker.ingest_bible(mem)
    print(f"Result: {msg}")
    
    # Check if facts were added
    if "facts" in mem.data and len(mem.data["facts"]) > 0:
        print(f"Facts in Memory: {len(mem.data['facts'])}")
        print(f"Sample Fact: {mem.data['facts'][-1]}")
        
        if "[BIBLE_VEC]" in mem.data['facts'][-1]:
            print("PASS: Vector embedding tag found.")
        else:
            print("FAIL: No vector tag found.")
    else:
        print("FAIL: No facts added.")

def test_auto_learner_routing():
    print("\n--- Testing AutoLearner Routing ---")
    mem = NeuralMemory("brain_memory.json")
    auto = AutoLearner(mem)
    
    # We can't easily force attempt_learning to pick a knowledge task without mocking
    # But we can call classify manually to confirm the component integration
    
    desc = "research common language phrases"
    classification = auto.classifier.classify(desc)
    print(f"AutoLearner Classifier check for '{desc}': {classification}")
    
    if classification == "KNOWLEDGE":
        print("PASS: AutoLearner has access to classifier.")
    else:
        print("FAIL: AutoLearner classifier mismatch.")
        
if __name__ == "__main__":
    test_meta_classifier()
    test_knowledge_embedding()
    test_auto_learner_routing()
