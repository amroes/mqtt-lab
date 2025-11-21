# Sensor Network

This directory implements the sensor network portion of the MQTT lab.

## Agents
- `sensor_agent.py` publishes sinusoidal readings per zone/type/sensor.
- `averaging_agent.py` subscribes to sensor topics, windows readings, and publishes averages.
- `interface_agent.py` renders a live dashboard of averages.
- `master.py` orchestrates the agents, spawns sensors and averaging agents, and keeps the dashboard updated.

## Running the Scenario

1. Start the MQTT broker (e.g., Mosquitto or shiftr.io).
2. From this directory:
   ```bash
   python sensor_agent.py --zone living_room --type temperature --id sensor_0
   python averaging_agent.py --zone living_room --type temperature
   python interface_agent.py
   python master.py
   ```
3. `master.py` spawns sensors/averagers dynamically and will maintain the dashboard until interrupted.

