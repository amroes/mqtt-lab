#!/usr/bin/env python3
"""Master process - spawns and manages agents dynamically."""

import random
import signal
import subprocess
import sys
import time

processes = []

def spawn_sensor(zone, mtype, sid):
    cmd = ["python3", "sensor_agent.py", "--zone", zone, "--type", mtype, "--id", sid]
    p = subprocess.Popen(cmd)
    processes.append(("sensor", sid, p))
    print(f"[MASTER] Spawned sensor {sid}")
    return p

def spawn_averaging(zone, mtype):
    cmd = ["python3", "averaging_agent.py", "--zone", zone, "--type", mtype]
    p = subprocess.Popen(cmd)
    processes.append(("avg", f"{zone}/{mtype}", p))
    print(f"[MASTER] Spawned averaging agent for {zone}/{mtype}")

def cleanup(sig=None, frame=None):
    for ptype, name, p in processes:
        p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

def main():
    zones = ["living_room", "bedroom", "kitchen"]
    types = ["temperature", "humidity"]
    
    # Spawn averaging agents
    for z in zones:
        for t in types:
            spawn_averaging(z, t)
    time.sleep(1)
    
    # Spawn initial sensors
    sensor_id = 0
    for z in zones:
        for t in types:
            for _ in range(2):
                spawn_sensor(z, t, f"sensor_{sensor_id}")
                sensor_id += 1
    
    # Spawn interface
    subprocess.Popen(["python3", "interface_agent.py"])
    
    # Dynamic behavior: add/remove sensors
    try:
        while True:
            time.sleep(15)
            # Randomly kill a sensor
            sensors = [(i, p) for i, (pt, n, p) in enumerate(processes) if pt == "sensor" and p.poll() is None]
            if sensors and random.random() < 0.3:
                idx, p = random.choice(sensors)
                p.terminate()
                print(f"[MASTER] Removed sensor")
            # Randomly add a sensor
            if random.random() < 0.4:
                z = random.choice(zones)
                t = random.choice(types)
                spawn_sensor(z, t, f"sensor_{sensor_id}")
                sensor_id += 1
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()

