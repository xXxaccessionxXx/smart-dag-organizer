
import os

def fix_imports():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for filename in os.listdir(current_dir):
        if filename.endswith(".py") and filename != "fix_imports.py":
            filepath = os.path.join(current_dir, filename)
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            if "sys.path.append" not in content and "import src" in content:
                print(f"Fixing {filename}...")
                new_content = "import sys\nimport os\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n\n" + content
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)

if __name__ == "__main__":
    fix_imports()
