import json
import os

from openpyxl import Workbook
from openai import OpenAI
from decouple import config

from helper_func import get_trading_setups_directory, print_status
from llm_prompts import SUMMARY_SYSTEM_PROMPT
from tqdm import tqdm

openai_model = config("EXTRACTION_MODEL")
openai_api_key = config("OPENAI_API_KEY")

symbols = json.loads(config("SYMBOLS"))
download_directory = os.path.join(os.path.expanduser("~"), "Downloads")


def summarize_trading_setups():
    workbook = Workbook()
    # Remove the default sheet created by Workbook
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    client = OpenAI(api_key=openai_api_key)

    for symbol in tqdm(symbols, desc="Processing symbols"):
        directory = get_trading_setups_directory(symbol)
        # Create a new sheet for each symbol and add header row
        sheet = workbook.create_sheet(title=symbol)
        sheet.append(["Filename", "Direction", "Entry", "Stop_Loss", "Take_Profit"])

        files = [f for f in os.listdir(directory) if f.lower().endswith(".txt")]
        for filename in tqdm(files, desc=f"Processing files for {symbol}", leave=False):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            response = client.ChatCompletion.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
            )
            summary_text = response.choices[0].message.content
            try:
                summary = json.loads(summary_text)
            except json.JSONDecodeError:
                # If parsing fails, fill with None values
                summary = {
                    "direction": None,
                    "entry": None,
                    "stop_loss": None,
                    "take_profit": None,
                }
            sheet.append(
                [
                    filename,
                    summary.get("direction"),
                    summary.get("entry"),
                    summary.get("stop_loss"),
                    summary.get("take_profit"),
                ]
            )

    save_path = os.path.join(download_directory, "trading_summaries.xlsx")
    workbook.save(save_path)
    print_status(f"Summaries written to {save_path}")


if __name__ == "__main__":
    summarize_trading_setups()
