#!/usr/bin/env python3
"""Machine agent - responds to CFPs, executes jobs."""

import argparse
import json
import threading
import time

import paho.mqtt.client as mqtt

BROKER, PORT = "localhost", 1883

class MachineAgent:
    def __init__(self, machine_id, capabilities):
        self.machine_id = machine_id
        self.capabilities = capabilities  # {job_type: time_to_complete}
        self.busy_until = 0
        self.lock = threading.Lock()
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client, userdata, flags, rc, props):
        client.subscribe("/cfp")  # Call for proposals
        client.subscribe(f"/assign/{self.machine_id}")  # Job assignments
        print(f"[MACHINE {self.machine_id}] Ready. Capabilities: {self.capabilities}")
    
    def _on_message(self, client, userdata, msg):
        data = json.loads(msg.payload.decode())
        
        if msg.topic == "/cfp":
            self._handle_cfp(data)
        elif msg.topic == f"/assign/{self.machine_id}":
            self._handle_assignment(data)
    
    def _handle_cfp(self, data):
        job_type = data["job_type"]
        cfp_id = data["cfp_id"]
        
        with self.lock:
            is_busy = time.time() < self.busy_until
        
        if is_busy:
            return  # Don't respond if busy
        
        if job_type in self.capabilities:
            bid = {
                "cfp_id": cfp_id,
                "machine_id": self.machine_id,
                "bid_time": self.capabilities[job_type],
                "status": "proposal"
            }
            print(f"[MACHINE {self.machine_id}] Bidding {bid['bid_time']}s for {job_type}")
        else:
            bid = {
                "cfp_id": cfp_id,
                "machine_id": self.machine_id,
                "status": "reject"
            }
            print(f"[MACHINE {self.machine_id}] Rejecting {job_type} (not capable)")
        
        self.client.publish("/bids", json.dumps(bid))
    
    def _handle_assignment(self, data):
        job_type = data["job_type"]
        duration = self.capabilities[job_type]
        
        with self.lock:
            self.busy_until = time.time() + duration
        
        print(f"[MACHINE {self.machine_id}] 🔧 Executing {job_type} for {duration}s")
        
        # Simulate job execution in background
        def complete_job():
            time.sleep(duration)
            print(f"[MACHINE {self.machine_id}] ✅ Completed {job_type}")
            self.client.publish("/job_complete", json.dumps({
                "machine_id": self.machine_id,
                "job_type": job_type
            }))
        
        threading.Thread(target=complete_job, daemon=True).start()
    
    def run(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--capabilities", required=True)  # JSON string
    args = parser.parse_args()
    
    caps = json.loads(args.capabilities)
    MachineAgent(args.id, caps).run()

