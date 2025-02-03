import os

from datetime import datetime
from decouple import config


def print_status(status):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}]: {status}")


def get_symbol_directory(symbol):
    base_dir = config("DOWNLOAD_DIRECTORY")
    return os.path.join(base_dir, symbol)


def get_trading_setups_directory(symbol):
    base_dir = config("DOWNLOAD_DIRECTORY")
    return os.path.join(base_dir, symbol, "trading_setups")


def save_trading_setup_to_file(symbol, trading_setup, file_name):
    if trading_setup is None or not trading_setup.strip():
        print_status(
            f"Warning: No content in trading setup for {file_name}. Skipping..."
        )
        return

    trading_setups_dir = get_trading_setups_directory(symbol)

    check_if_directory_exists(trading_setups_dir)

    file_path = os.path.join(trading_setups_dir, file_name + ".txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(trading_setup)


def check_if_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
