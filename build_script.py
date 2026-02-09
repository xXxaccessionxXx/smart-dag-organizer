
import sys
import os
import subprocess
import shutil

def install_pyinstaller():
    print("Checking PyInstaller...")
    try:
        import PyInstaller
        print(f"PyInstaller found: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install PyInstaller: {e}")
            return False

def clean_build():
    for d in ['build', 'dist']:
        if os.path.exists(d):
            print(f"Cleaning {d}...")
            try:
                shutil.rmtree(d)
            except Exception as e:
                print(f"Error cleaning {d}: {e}")

def run_build():
    print("Starting build process...")
    # Use PyInstaller as module to avoid path issues
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "main.spec"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Stream output
        with open("build_log.txt", "w") as f:
            for line in process.stdout:
                sys.stdout.write(line)
                f.write(line)
                
        process.wait()
        
        if process.returncode == 0:
            print("\nBuild successful! Executable in dist/SmartDAGOrganizer")
        else:
            print(f"\nBuild failed with return code {process.returncode}")
            
    except Exception as e:
        print(f"Error running build: {e}")

if __name__ == "__main__":
    if install_pyinstaller():
        clean_build()
        run_build()
    else:
        print("Cannot proceed without PyInstaller.")
