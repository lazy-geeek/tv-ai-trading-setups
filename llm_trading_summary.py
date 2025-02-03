import json
import os

from openai import OpenAI
from decouple import config

from helper_func import get_trading_setups_directory
from llm_prompts import SUMMARY_SYSTEM_PROMPT

openai_model = config("EXTRACTION_MODEL")
openai_api_key = config("OPENAI_API_KEY")

symbols = json.loads(config("SYMBOLS"))


def summarize_trading_setups():
    directory = get_trading_setups_directory()
    summaries = {}
    client = OpenAI(api_key=openai_api_key)
    for symbol in symbols:
        file_path = os.path.join(directory, f"{symbol}.txt")
        if not os.path.exists(file_path):
            print(f"File for {symbol} not found: {file_path}")
            continue
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
        summaries[symbol] = summary_text
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    summarize_trading_setups()
