#!/usr/bin/env python3
"""
Processor Loop - Runs process_all_data.py every 15 minutes
"""
import time
import subprocess
import sys
from datetime import datetime

def main():
    """Run processor in infinite loop"""
    while True:
        try:
            print(f"[Processor] Running at {datetime.now()}")
            
            # Run the processor
            result = subprocess.run(
                [sys.executable, "scripts/process_all_data.py"],
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print("[Processor] Completed successfully")
            else:
                print(f"[Processor] Failed with exit code {result.returncode}")
            
            print("[Processor] Next run in 15 minutes...")
            time.sleep(900)  # 15 minutes
            
        except KeyboardInterrupt:
            print("\n[Processor] Stopped by user")
            break
        except Exception as e:
            print(f"[Processor] Error: {e}")
            print("[Processor] Retrying in 1 minute...")
            time.sleep(60)

if __name__ == "__main__":
    main()
