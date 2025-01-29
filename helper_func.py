from datetime import datetime


def print_status(status):

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{timestamp}]: {status}")
