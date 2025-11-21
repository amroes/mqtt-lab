# Contract Net Protocol

This directory demonstrates a simple contract net using MQTT.

## Agents
- `machine_agent.py` responds to CFPs, bids according to its capabilities, and reports job completion.
- `supervisor.py` issues CFPs, collects bids, selects winners, and assigns jobs.
- `master.py` spawns machines and the supervisor to run the demo.

## Running

```bash
python machine_agent.py --id M1 --capabilities '{"assembly": 5, "welding": 8}'
python machine_agent.py --id M2 --capabilities '{"assembly": 6, "painting": 4}'
python machine_agent.py --id M3 --capabilities '{"welding": 7, "testing": 3}'
python machine_agent.py --id M4 --capabilities '{"painting": 5, "testing": 4, "packaging": 2}'
python supervisor.py
python master.py
```

`master.py` coordinates the entire demo, ensuring the supervisor and machines run together.

