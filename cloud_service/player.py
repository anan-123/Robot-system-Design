import zmq
import zmq.asyncio
import asyncio
import json
import sys
import sys,os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.config import ZMQ_TOKEN

robot_id = sys.argv[1]
PUB_PORT = int(sys.argv[2])
SUB_PORT = int(sys.argv[3])


TOPIC_SENSOR = f"robot/{robot_id}/sensor"
TOPIC_COMMAND = f"robot/{robot_id}/command"
TOPIC_PROCESSED = f"robot/{robot_id}/processed"
TOPIC_STATUS = f"robot/{robot_id}/status"

context = zmq.asyncio.Context()

pub = context.socket(zmq.PUB)
sub = context.socket(zmq.SUB)

pub.bind(f"tcp://*:{PUB_PORT}")
sub.bind(f"tcp://*:{SUB_PORT}")

sub.setsockopt_string(zmq.SUBSCRIBE, "")

print(f"Player Running for {robot_id}")

async def handle():
    while True:
        topic, msg = await sub.recv_multipart()
        topic_str = topic.decode()
        data = json.loads(msg.decode())
        if data.get("token") != ZMQ_TOKEN:
            print(f"Rejected unauthorized access on {topic_str}")
            continue

        print(f"Player RECEIVED [{topic_str}]: {data}")

        # Robot → User
        if topic_str == TOPIC_SENSOR:
            await pub.send_multipart([
                TOPIC_PROCESSED.encode(),
                json.dumps(data).encode()
            ])
       
        # User  → Robot
        elif topic_str == TOPIC_COMMAND:
            await pub.send_multipart([
                TOPIC_COMMAND.encode(),
                json.dumps(data).encode()
            ])

        # broadcast to user, player,robot
        elif topic_str == TOPIC_STATUS:
            await pub.send_multipart([
                TOPIC_STATUS.encode(),
                json.dumps(data).encode()
            ])

        else:
            print(f"Unknown topic: {topic_str}")

asyncio.run(handle())



