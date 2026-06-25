from time import sleep

counter = 0


def run(shared_state: dict):
    global counter

    while True:
        sleep(3)
        shared_state["status_msg"] = f"searching for '{counter}'"
        shared_state["exchange_rate"] = 0.00649
        counter += 1
