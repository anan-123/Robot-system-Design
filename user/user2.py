import asyncio
import aiohttp
import zmq
import zmq.asyncio
import json
import time
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.config import CLOUD_URL
ZMQ_TOKEN = "deliberate_wrong_token"
context = zmq.asyncio.Context()
# change this according to the robot settings
cmds_allowed = ["forward", "backward", "stop", "status", "left", "right"]

async def main():
    async with aiohttp.ClientSession() as session:

        robots = await (await session.get(f"{CLOUD_URL}/robots")).json()

        print("List of Robots:", robots)

        robot_id = input("Enter robot id: ")
        while robot_id not in robots:
            robot_id = input("Enter correct robot id: ")

      #  resp = await session.post(f"{CLOUD_URL}/connect/{robot_id}",headers={"user_token": ZMQ_TOKEN})
        resp = await session.post(
    f"{CLOUD_URL}/connect/{robot_id}",
    headers={"user-token": ZMQ_TOKEN}
)
        

        info = await resp.json()
        print("[User] Connect response:", info) 

        pub = context.socket(zmq.PUB)
        sub = context.socket(zmq.SUB)

  
        pub.connect(f"tcp://127.0.0.1:{info['sub_port']}")
        sub.connect(f"tcp://127.0.0.1:{info['pub_port']}")

        await asyncio.sleep(1)
      
        sub.setsockopt_string(zmq.SUBSCRIBE, f"robot/{robot_id}/")

    
        async def receive():
            # receive data from robot
            while True:
                topic, msg = await sub.recv_multipart()
                data = json.loads(msg.decode())

                print(f"RECEIVED [{topic.decode()}]: {data}")
                if "timestamp" in data:
                    latency_ms = (time.time() - data["timestamp"]) * 1000
                    print(f"latency: {latency_ms:.1f}ms")

        
        async def send():
            # send commands to robot
            loop = asyncio.get_event_loop()

            while True:
                cmd = await loop.run_in_executor(None, input, "Command: ")

                if cmd not in cmds_allowed:
                    print(" Invalid command")
                    continue

                topic = f"robot/{robot_id}/command"

                await pub.send_multipart([
                    topic.encode(),
                    json.dumps({
                        "command": cmd,
                        "speed": 0.5,
                        "token":ZMQ_TOKEN
                    }).encode()
                ])

                print("SENT:", cmd)

        await asyncio.gather(receive(), send())


asyncio.run(main())