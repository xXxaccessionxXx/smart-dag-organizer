
from create_installer import generate_ico
import os
import sys

log_file = "test_log.txt"

def log(msg):
    with open(log_file, "a") as f:
        f.write(msg + "\n")

if os.path.exists(log_file):
    try: os.remove(log_file)
    except: pass

log("Starting test...")
test_file = "assets/test_pillow.ico"
if os.path.exists(test_file):
    try: os.remove(test_file)
    except: pass

try:
    # We need to capture stdout from generate_ico? 
    # generate_ico prints to stdout. We can redirect stdout?
    # Or just rely on the fact that if it fails, it prints exception.
    # Let's try redirection.
    from io import StringIO
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    generate_ico(test_file)
    
    sys.stdout = old_stdout
    log(mystdout.getvalue())

    if os.path.exists(test_file) and os.path.getsize(test_file) > 1000:
        log("[SUCCESS] Pillow generated valid ICO.")
    else:
        log("[FAILURE] Icon file missing or too small.")
        
except Exception as e:
    log(f"[FAILURE] Script crashed: {e}")

