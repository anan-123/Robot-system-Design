# P2P robot design
 
A p2p triangle system using ZMQ pub/sub messaging with a cloud broker. Supports multiple robots, token-based security, and latency monitoring.
 
 
## Architecture
 
```
image
Robot (r2.py) ←→ Player (player.py) ←→ Cloud (cloud.py) ←→ User (u2.py)
```
 
- **Cloud** — FastAPI server that registers robots, spawns players, and handles user connections
- **Player** — ZMQ broker spawned per robot, routes messages between robot and user
- **Robot** — Runs on JetBot, publishes sensor data and receives commands
- **User** — CLI client to send commands and receive sensor data from a robot
 
---
## Project Structure
 
```
project/
├── config/
│   └── config.py           # shared config (ports, URLs, tokens)
├── cloud_service/
│   ├── cloud.py            # FastAPI cloud server
│   └── player.py           # ZMQ message broker (spawned per robot)
├── robot/
│   └── r2.py               # robot client (runs on JetBot)
├── user/
│   └── u2.py               # user CLI client
└── requirements.txt
```
 
---
Install dependencies:
```bash
pip install -r requirements.txt
```
or
```bash
pip install fastapi uvicorn aiohttp pyzmq
```

## How to Run
 
Run in this order:
 
**1. Start the cloud server** 
```bash
python .\cloud_service\cloud.py
```
 
**2. Start the robot**
```bash
python .\robot\robot.py <robot_id>
```

For multiple robots use:
```bash
./run_robots.sh 
```
 
**3. Start the user** :
```bash
python .\user\user.py 
```
Then enter the robot id when prompted and start sending commands.The sensor values from the robot will be printed so just enter command without spaces and not worry on the input looking weird on terminal.
 
---


## Configuration — config.py:
Set these:
CLOUD_URL
BASE_PORT
ZMQ_TOKEN
## Security
 
- **HTTP** — all `/connect` requests require a `user-token` header matching `ZMQ_TOKEN`
- **ZMQ** — every message includes a token field, rejected by the player if wrong
- Unauthorized users cannot get port info or publish/subscribe to any topic

#### Latency Monitoring
 
The user client automatically prints latency for every received sensor message:
```
e.g. latency: 5.3ms
```
 
This is measured as the time between the robot sending the message and the user receiving it. Useful for diagnosing network issues.

#### Testing
Change number of robots to spawn in run_robot.sh. Currently set to 25 robots.

#### Scaling beyond Local system
Change cloud url to public url. And change CLOUD_HOST IP. If all three player, user and robot are not in same network then the urls must be public exposed or have a cloud relay based system.ss

## System Design and Testing
More detailed explanations and discussion for choices, testing and scalability can be found in the writeup.pdf file.

