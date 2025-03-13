import os
import shutil

from datetime import datetime
from decouple import config
from tqdm import tqdm
from werkzeug.utils import secure_filename


def print_status(status):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    tqdm.write(f"[{timestamp}]: {status}")


def get_download_directory():
    base_dir = config("DOWNLOAD_DIRECTORY")

    check_if_directory_exists(base_dir)

    return base_dir


def get_symbol_directory(symbol):
    base_dir = config("DOWNLOAD_DIRECTORY")
    symbol_dir = os.path.join(base_dir, symbol)

    check_if_directory_exists(symbol_dir)

    return symbol_dir


def get_trading_setups_directory(symbol):
    base_dir = config("DOWNLOAD_DIRECTORY")
    trading_setup_dir = os.path.join(base_dir, symbol, "trading_setups")

    check_if_directory_exists(trading_setup_dir)

    return trading_setup_dir


def save_trading_setup_to_file(symbol, trading_setup, file_name):
    if trading_setup is None or not trading_setup.strip():
        print_status(
            f"Warning: No content in trading setup for {file_name}. Skipping..."
        )
        return

    trading_setups_dir = get_trading_setups_directory(symbol)

    safe_file_name = secure_filename(file_name)
    file_path = os.path.join(trading_setups_dir, safe_file_name + ".txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(trading_setup)


def check_if_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def clear_download_directory():
    # Delete all files from download directory
    download_directory = get_download_directory()
    for filename in os.listdir(download_directory):
        file_path = os.path.join(download_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print_status("Failed to delete %s. Reason: %s" % (file_path, e))
