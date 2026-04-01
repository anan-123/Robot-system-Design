
import asyncio
import subprocess
from fastapi import FastAPI,Header
import uvicorn
import time
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.config import BASE_PORT, ZMQ_TOKEN


app = FastAPI()

#path to player file
script_path = os.path.join(os.path.dirname(__file__), "player.py")
if not os.path.exists(script_path):
    raise RuntimeError(f"player not found at {script_path}")

robots = {}  # robot_id : { "last_seen": float, "pub_port": int, "sub_port": int }


# This function spawns a player for every active robot
@app.post("/register/{robot_id}")
async def register(robot_id: str):
    print(f"Registering {robot_id}")
    # duplicate registration
    if robot_id in robots:
        return {"pub_port": robots[robot_id]["pub_port"],
            "sub_port": robots[robot_id]["sub_port"], "status": "already_registered"}
    # for production servers with concurrent requests with ms difference. If registering sequentially not needed
        # used_ports = {v["pub_port"] for v in robots.values()}
        # pub_port = BASE_PORT
        # while pub_port in used_ports:
            #     pub_port += 2
    pub_port = BASE_PORT + len(robots) * 2
    sub_port = pub_port + 1

    try:
        subprocess.Popen([
            "python", script_path,
            robot_id,
            str(pub_port),
            str(sub_port)
        ])
    except Exception as e:
        return {"error": f"Player spawn failed: {e}"}, 500

    robots[robot_id] = {
        "last_seen": time.time(),
        "pub_port": pub_port,
        "sub_port": sub_port
    }

    return {"pub_port": pub_port, "sub_port": sub_port}


@app.post("/heartbeat/{robot_id}")
async def heartbeat(robot_id: str):
    if robot_id not in robots:
        return {"status": "unknown robot"}
    robots[robot_id]["last_seen"] = time.time()
    print(f"Heartbeat from {robot_id}")
    return {"status": "ok"}


@app.get("/robots")
async def get_robots():
    return list(robots.keys())

#cleanup robot process
@app.post("/deregister/{robot_id}")
async def deregister(robot_id: str):
    if robot_id not in robots:
        return
    pid = robots[robot_id].get("pid")
    if pid:
        import signal, os
        try: os.kill(pid, signal.SIGTERM)
        except ProcessLookupError: pass
    del robots[robot_id]
    return {"status": "removed"}

@app.post("/connect/{robot_id}")
async def connect(robot_id: str, user_token: str = Header(...)):
    if user_token != ZMQ_TOKEN:
       return {"error":f"Not authorized to connect to robot"},404
    if robot_id not in robots:
        return {"error": f"Robot '{robot_id}' not registered"}, 404

    return {
        "status": "connected",
        "pub_port": robots[robot_id]["pub_port"],
        "sub_port": robots[robot_id]["sub_port"]
    }



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)