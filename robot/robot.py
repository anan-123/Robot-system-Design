import asyncio
import aiohttp
import zmq
import zmq.asyncio
import json
import time
import sys
from jetbot import Robot
import sys,os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.config import CLOUD_URL,ZMQ_TOKEN

robot = Robot()

if len(sys.argv) < 2:
    print("Right format for running code: r2.py robot_id"); sys.exit(1)
robot_id = sys.argv[1]

TOPIC_SENSOR = f"robot/{robot_id}/sensor"
TOPIC_COMMAND = f"robot/{robot_id}/command"
TOPIC_STATUS = f"robot/{robot_id}/status"

print("The robot id:", robot_id)

context = zmq.asyncio.Context()
pub = context.socket(zmq.PUB)
sub = context.socket(zmq.SUB)


async def heartbeat():
    # send hearbeat to robot
    while True:
        await asyncio.sleep(5)
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(f"{CLOUD_URL}/heartbeat/{robot_id}")
            print("Heartbeat sent")
        except aiohttp.ClientError as e:
            print(f"Heartbeat failed: {e}")



async def sensor(pub):
    # publish sensor data
    while True:
        data = {
            "robot_id": robot_id,
            "token": ZMQ_TOKEN,
            "state": robot.get_state(), 
            "timestamp": time.time()
        }
        try:
            await pub.send_multipart([
            TOPIC_SENSOR.encode(),
            json.dumps(data).encode()
        ])
        except zmq.ZMQError as e:
            print(f"Failed to send to sensor topic: {e}")
        await asyncio.sleep(1)
        
#change this as per the robot settings
async def apply_commands(speed, command):
        print(f"EXECUTE: {command}")

        if command == "forward":
            robot.forward(speed)

        elif command == "backward":
            robot.backward(speed)

        elif command == "left":
            robot.left(speed)

        elif command == "right":
            robot.right(speed)

        elif command == "stop":
            robot.stop()

        elif command == "status":
            status_msg = {
                "robot_id": robot_id,
                "token":ZMQ_TOKEN,
                "source": "robot",
                "status": "active",
                "timestamp": time.time()
            }

            await pub.send_multipart([
                TOPIC_STATUS.encode(),
                json.dumps(status_msg).encode()
            ])

        else:
            print("Unknown command:", command)

async def receive(sub):
    # receive data and execute commands
    while True:
        topic, msg = await sub.recv_multipart()
        topic_str = topic.decode()
        data = json.loads(msg.decode())

        # Only act on command topic
        if topic_str != TOPIC_COMMAND:
            continue

        command = data.get("command")
        speed = data.get("speed", 0.5)
        await apply_commands(speed,command)
        



async def main():
    # try 3 times to register robot
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.post(f"{CLOUD_URL}/register/{robot_id}", timeout=5)
                info = await resp.json(); break
        except Exception as e:
            print(e)

    # async with aiohttp.ClientSession() as session:
    #     resp = await session.post(f"{CLOUD_URL}/register/{robot_id}")
    #     info = await resp.json()

    # Connect to player (pub, sub server)
    sub.connect(f"tcp://127.0.0.1:{info['pub_port']}")
    pub.connect(f"tcp://127.0.0.1:{info['sub_port']}")

    sub.setsockopt_string(zmq.SUBSCRIBE, "")
    await asyncio.gather(
        heartbeat(),
        sensor(pub),
        receive(sub)
    )

asyncio.run(main())