# MQTT Multi-Agent Systems Lab

This repository collects the MQTT lab deliverables described in `mqtt-lab-report.md` and `consignes.md`.

## Structure
- `Part1_Basics/`: MQTT handshake, basic publish/subscribe, and ping-pong exercises. See the directory README for usage.
- `SensorNetwork/`: Sensor, averaging, interface agents, and a master orchestrator that demonstrates dynamic behavior.
- `AnomalyDetection/`: Builds on the sensor network with anomaly detection, identification, and a faulty sensor tester.
- `ContractNet/`: Implements the Contract Net protocol with machine agents, a supervisor, and a coordinating master.
- `requirements.txt`: Python dependencies (`paho-mqtt`).
- `mqtt-lab-report.md`: Final report with technical choices, highlights, execution traces, and reflections.

## Setup

```bash
python -m venv .venv
.venv\\Scripts\\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt
```

Make sure an MQTT broker is running (e.g., Mosquitto on `localhost:1883` or shiftr.io).

## How to Run

- **Part 1 (Basics)**  
  ```powershell
  cd Part1_Basics
  python first_client.py
  ```
  or launch the ping-pong agents together:
  ```bash
  cd Part1_Basics
  ./start_ping_pong.sh
  ```
  (Windows PowerShell: run `python ping_pong.py ping --start` and `python ping_pong.py pong` in **two separate shells**.)

- **Part 2 (Sensor Network)**  
  Start the orchestrator, which spawns averaging agents, sensors, and the interface dashboard:
  ```bash
  cd SensorNetwork
  python master.py
  ```
  To launch agents manually, open three terminals (sensor, averaging, interface) and run in each:
  ```bash
  python sensor_agent.py --zone living_room --type temperature --id sensor_0 --interval 2.0
  python averaging_agent.py --zone living_room --type temperature --window 10 --interval 5
  python interface_agent.py
  ```

- **Part 2.3 (Anomaly Detection)**  
  Run each agent in its own shell:
  ```bash
  cd AnomalyDetection
  python sensor_agent.py --zone kitchen --type temperature --id sensor_faulty --interval 2.0
  python detection_agent.py
  python identification_agent.py
  python faulty_sensor.py --zone kitchen --type temperature --id faulty_1 --fault_magnitude 50
  ```
  Adjust `--fault_magnitude` or `--interval` to test different fault patterns.

- **Part 3 (Contract Net)**  
  Each machine and the supervisor expect JSON capability maps; the master script launches them for you:
  ```bash
  cd ContractNet
  python master.py
  ```
  To run individual machines:
  ```bash
  python machine_agent.py --id M1 --capabilities '{"assembly": 5, "welding": 8}'
  python supervisor.py
  ```

Each directory also provides a README with deeper documentation about parameters, expected outputs, and troubleshooting tips.

