import os
import json

from decouple import config
from tqdm import tqdm
from pprint import pprint

from helper_func import print_status, save_trading_setup_to_file, get_symbol_directory


symbols = json.loads(config("SYMBOLS"))


for symbol in symbols:
    print(get_symbol_directory(symbol))
