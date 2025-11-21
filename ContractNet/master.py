#!/usr/bin/env python3
"""Master - spawns machines and supervisor."""

import json
import signal
import subprocess
import sys
import time

processes = []

def cleanup(sig=None, frame=None):
    for p in processes:
        p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

def main():
    machines = [
        ("M1", {"assembly": 5, "welding": 8}),
        ("M2", {"assembly": 6, "painting": 4}),
        ("M3", {"welding": 7, "testing": 3}),
        ("M4", {"painting": 5, "testing": 4, "packaging": 2}),
    ]
    
    # Spawn machines
    for mid, caps in machines:
        cmd = ["python3", "machine_agent.py", "--id", mid, "--capabilities", json.dumps(caps)]
        processes.append(subprocess.Popen(cmd))
        print(f"[MASTER] Spawned {mid}")
    
    time.sleep(2)
    
    # Spawn supervisor
    processes.append(subprocess.Popen(["python3", "supervisor.py"]))
    
    # Wait for completion
    for p in processes:
        p.wait()

if __name__ == "__main__":
    main()

