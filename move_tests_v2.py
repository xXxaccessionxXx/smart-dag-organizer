
import os
import shutil
import glob
import sys

def move_files():
    print(f"Current Working Directory: {os.getcwd()}", flush=True)
    target_dir = "tests"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    patterns = [
        "test_*.py",
        "test_*.txt",
        "verify_*.py",
        "verify_*.txt",
        "reproduce_crash.py",
        "trace_import.py"
    ]

    moved_count = 0
    for pattern in patterns:
        print(f"Checking pattern: {pattern}", flush=True)
        files = glob.glob(pattern)
        print(f"Found {len(files)} files matching {pattern}", flush=True)
        
        for filepath in files:
            try:
                filename = os.path.basename(filepath)
                dest = os.path.join(target_dir, filename)
                
                print(f"Attempting to move {filename} to {dest}...", flush=True)
                
                # If destination exists, remove it first (overwrite)
                if os.path.exists(dest):
                    print(f"Destination {dest} exists, removing...", flush=True)
                    os.remove(dest)
                    
                shutil.move(filepath, target_dir)
                print(f"Moved: {filename}", flush=True)
                moved_count += 1
            except Exception as e:
                print(f"Error moving {filepath}: {e}", flush=True)

    print(f"Total files moved: {moved_count}", flush=True)

if __name__ == "__main__":
    move_files()
