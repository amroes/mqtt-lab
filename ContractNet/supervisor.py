#!/usr/bin/env python3
"""Supervisor agent - issues CFPs, assigns jobs."""

import json
import random
import threading
import time

import paho.mqtt.client as mqtt

BROKER, PORT = "localhost", 1883
DEADLINE = 3.0  # Seconds to wait for bids

class SupervisorAgent:
    def __init__(self, job_queue):
        self.job_queue = job_queue
        self.current_cfp = None
        self.bids = []
        self.lock = threading.Lock()
        self.cfp_counter = 0
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client, userdata, flags, rc, props):
        client.subscribe("/bids")
        client.subscribe("/job_complete")
        print("[SUPERVISOR] Connected and ready")
    
    def _on_message(self, client, userdata, msg):
        data = json.loads(msg.payload.decode())
        
        if msg.topic == "/bids":
            with self.lock:
                if self.current_cfp and data.get("cfp_id") == self.current_cfp["cfp_id"]:
                    self.bids.append(data)
        elif msg.topic == "/job_complete":
            print(f"[SUPERVISOR] Job completed by {data['machine_id']}")
    
    def issue_cfp(self, job_type):
        self.cfp_counter += 1
        cfp = {"cfp_id": self.cfp_counter, "job_type": job_type}
        
        with self.lock:
            self.current_cfp = cfp
            self.bids = []
        
        print(f"\n[SUPERVISOR] 📢 CFP #{self.cfp_counter}: {job_type}")
        self.client.publish("/cfp", json.dumps(cfp))
        
        # Wait for deadline
        time.sleep(DEADLINE)
        
        with self.lock:
            proposals = [b for b in self.bids if b.get("status") == "proposal"]
            rejections = [b for b in self.bids if b.get("status") == "reject"]
        
        print(f"[SUPERVISOR] Received {len(proposals)} proposals, {len(rejections)} rejections")
        
        if proposals:
            # Select best bid (lowest time)
            best = min(proposals, key=lambda x: x["bid_time"])
            print(f"[SUPERVISOR] ✓ Selected {best['machine_id']} (bid: {best['bid_time']}s)")
            
            # Send assignment to winner
            self.client.publish(f"/assign/{best['machine_id']}", json.dumps({
                "job_type": job_type,
                "cfp_id": self.cfp_counter
            }))
            
            # Notify losers
            for bid in proposals:
                if bid["machine_id"] != best["machine_id"]:
                    self.client.publish(f"/reject/{bid['machine_id']}", json.dumps({
                        "cfp_id": self.cfp_counter
                    }))
            
            return True
        else:
            print(f"[SUPERVISOR] ✗ No proposals received for {job_type}")
            return False
    
    def run(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()
        time.sleep(1)  # Wait for machines
        
        for job in self.job_queue:
            self.issue_cfp(job)
            time.sleep(1)  # Gap between CFPs
        
        print("\n[SUPERVISOR] All jobs dispatched. Waiting for completion...")
        time.sleep(10)
        self.client.disconnect()

if __name__ == "__main__":
    jobs = ["assembly", "welding", "painting", "testing", "assembly", "welding", "packaging"]
    SupervisorAgent(jobs).run()

