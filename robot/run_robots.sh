#!/bin/bash

NUM_ROBOTS=25

cleanup() {
  echo "Stopping all robots..."
  kill 0
}

trap cleanup EXIT

echo "Starting $NUM_ROBOTS robots..."

for i in $(seq 1 $NUM_ROBOTS)
do
  ROBOT_ID="r$i"

  echo "Starting $ROBOT_ID"

  python robot.py "$ROBOT_ID" &
  sleep 0.2
done

wait