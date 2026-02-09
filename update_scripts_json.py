
import json
import os

def update_json():
    scripts_file = "data/genesis_scripts.json"
    
    # helper to read file content safely
    def read_content(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    files_to_sync = {
        "launcher.py": "src/launcher.py",
        "workflow_organizer.py": "src/workflow_organizer.py",
        "script_library.py": "src/script_library.py"
    }

    if not os.path.exists(scripts_file):
        print(f"Error: {scripts_file} not found.")
        return

    try:
        with open(scripts_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    print("Updating scripts...")
    for key, source_path in files_to_sync.items():
        if os.path.exists(source_path):
            content = read_content(source_path)
            if key in data:
                data[key]["content"] = content
                print(f"Updated {key} from {source_path}")
            else:
                # Add if missing, default to Python
                data[key] = {"content": content, "language": "Python"}
                print(f"Added {key} from {source_path}")
        else:
            print(f"Warning: Source {source_path} not found.")

    try:
        with open(scripts_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("Success: genesis_scripts.json updated.")
    except Exception as e:
        print(f"Error writing JSON: {e}")

if __name__ == "__main__":
    update_json()
