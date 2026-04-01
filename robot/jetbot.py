import time
class Robot:
    def __init__(self):
        self.speed = 0.5
        self.state = "stopped"

    def set_motors(self, left_speed, right_speed):
        print(f"Motors -> Left: {left_speed}, Right: {right_speed}")

    def forward(self, speed=0.5):
        self.state = "forward"
        self.set_motors(speed, speed)

    def backward(self, speed=0.5):
        self.state = "backward"
        self.set_motors(-speed, -speed)

    def left(self, speed=0.5):
        self.state = "left"
        self.set_motors(-speed, speed)

    def right(self, speed=0.5):
        self.state = "right"
        self.set_motors(speed, -speed)

    def stop(self):
        self.state = "stopped"
        self.set_motors(0, 0)

    def get_state(self):
        return {
            "state": self.state,
            "speed": self.speed
        }