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

    summaries = {}
    client = OpenAI(api_key=openai_api_key)

    # Process all text files in the trading setups directory

    for symbol in symbols:
        directory = get_trading_setups_directory(symbol)
        for filename in os.listdir(directory):
            if filename.lower().endswith(".txt"):
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
            summaries[filename] = summary_text
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    summarize_trading_setups()
