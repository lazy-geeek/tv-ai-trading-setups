import json
import os

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openai import OpenAI
from decouple import config

from helper_func import (
    get_download_directory,
    get_trading_setups_directory,
    print_status,
)
from llm_prompts import SUMMARY_SYSTEM_PROMPT
from tqdm import tqdm

openai_model = config("EXTRACTION_MODEL")
openai_api_key = config("OPENAI_API_KEY")

symbols = json.loads(config("SYMBOLS"))
download_directory = get_download_directory()


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
            response = client.chat.completions.create(
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
                    os.path.splitext(filename)[0],
                    summary.get("direction"),
                    summary.get("entry"),
                    summary.get("stop_loss"),
                    summary.get("take_profit"),
                ]
            )

    # Apply formatting to all sheets after processing
    for sheet in workbook.worksheets:
        # Bold header row cells
        for cell in sheet[1]:
            cell.font = Font(bold=True)
        # Bold first column cells
        for row in sheet.iter_rows(min_col=1, max_col=1):
            for cell in row:
                cell.font = Font(bold=True)
        # Auto-size columns
        for col in sheet.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            adjusted_width = max_length + 2
            sheet.column_dimensions[col_letter].width = adjusted_width
    save_path = os.path.join(download_directory, "trading_summaries.xlsx")
    if os.path.exists(save_path):
        os.remove(save_path)
    workbook.save(save_path)
    print_status(f"Summaries written to {save_path}")
