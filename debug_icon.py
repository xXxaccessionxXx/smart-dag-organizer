import sys
import os

# Redirect stdout and stderr to a file
sys.stdout = open("debug_output.txt", "w")
sys.stderr = sys.stdout

# Ensure modules can be imported from current directory
sys.path.append(os.getcwd())

print("Starting debug script...")
try:
    from create_installer import generate_ico
    print("Imported generate_ico successfully.")
    
    generate_ico("assets/icon.ico")
    print("generate_ico completed successfully.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    sys.stdout.close()
