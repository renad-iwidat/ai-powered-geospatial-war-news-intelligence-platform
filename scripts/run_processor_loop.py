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
    print("[Processor] Starting loop...")
    
    while True:
        try:
            print(f"\n[Processor] Running at {datetime.now()}")
            print("=" * 80)
            
            # Run the processor
            result = subprocess.run(
                [sys.executable, "scripts/process_all_data.py"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode == 0:
                print("[Processor] ✅ Completed successfully")
            else:
                print(f"[Processor] ❌ Failed with exit code {result.returncode}")
            
            print("[Processor] Next run in 15 minutes...")
            print("=" * 80)
            time.sleep(900)  # 15 minutes
            
        except subprocess.TimeoutExpired:
            print("[Processor] ⏱️ Timeout after 10 minutes - restarting...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n[Processor] Stopped by user")
            break
            
        except Exception as e:
            print(f"[Processor] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print("[Processor] Retrying in 1 minute...")
            time.sleep(60)

if __name__ == "__main__":
    main()
