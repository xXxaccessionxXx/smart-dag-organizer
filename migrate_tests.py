
import os
import shutil
import glob

def migrate():
    log_file = "migration_status.txt"
    target_dir = "tests"
    
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        with open(log_file, "w") as f:
            f.write("Migration Started\n")
            f.write(f"CWD: {os.getcwd()}\n")

        patterns = [
            "test_*.py",
            "test_*.txt",
            "verify_*.py",
            "verify_*.txt",
            "reproduce_crash.py",
            "trace_import.py"
        ]

        all_files = []
        for p in patterns:
            all_files.extend(glob.glob(p))
            
        with open(log_file, "a") as f:
            f.write(f"Found {len(all_files)} files to move.\n")

        for filepath in all_files:
            filename = os.path.basename(filepath)
            dest = os.path.join(target_dir, filename)
            
            try:
                if os.path.exists(dest):
                    os.remove(dest) # Force overwrite
                
                shutil.move(filepath, dest)
                with open(log_file, "a") as f:
                    f.write(f"Moved: {filename}\n")
            except Exception as e:
                with open(log_file, "a") as f:
                    f.write(f"Failed to move {filename}: {e}\n")

        with open(log_file, "a") as f:
            f.write("Migration Completed\n")

    except Exception as e:
        # Fallback if we can't write to log for some reason
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    migrate()
