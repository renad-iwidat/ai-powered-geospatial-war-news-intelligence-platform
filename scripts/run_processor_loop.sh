#!/bin/sh

# Processor Loop - Runs every 15 minutes
while true; do
    echo "[Processor] Running at $(date)"
    python scripts/process_all_data.py
    echo "[Processor] Completed. Next run in 15 minutes..."
    sleep 900
done
