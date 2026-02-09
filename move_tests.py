
import os
import shutil
import glob

def move_files():
    target_dir = "tests"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    patterns = [
        "test_*",
        "verify_*",
        "reproduce_crash.py",
        "trace_import.py"
    ]

    moved_count = 0
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            try:
                filename = os.path.basename(filepath)
                dest = os.path.join(target_dir, filename)
                
                # If destination exists, remove it first (overwrite)
                if os.path.exists(dest):
                    os.remove(dest)
                    
                shutil.move(filepath, target_dir)
                print(f"Moved: {filename}")
                moved_count += 1
            except Exception as e:
                print(f"Error moving {filepath}: {e}")

    print(f"Total files moved: {moved_count}")

if __name__ == "__main__":
    move_files()
