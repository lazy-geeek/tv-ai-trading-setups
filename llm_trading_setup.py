"""Trading setup generation using OpenRouter LLMs only."""

import base64
import os
import json

from glob import glob
from openai import OpenAI
from decouple import config
from tqdm import tqdm

# from pprint import pprint

from llm_prompts import *
from helper_func import print_status, save_trading_setup_to_file, get_symbol_directory

symbols = json.loads(config("SYMBOLS"))

openrouter_api_key = config("OPENROUTER_API_KEY")
openrouter_base_url = "https://openrouter.ai/api/v1"

# Load OpenRouter models from .env as a JSON list string
try:
    openrouter_models_raw = config("OPENROUTER_MODELS")
    openrouter_models = json.loads(openrouter_models_raw)
    if not isinstance(openrouter_models, list):
        raise ValueError("OPENROUTER_MODELS is not a valid JSON list")
except Exception as e:
    print_status(f"Error loading or parsing OPENROUTER_MODELS from .env: {e}")
    openrouter_models = []

system_prompt = TRADING_SYSTEM_PROMPT
user_prompt = TRADING_USER_PROMPT


def generate_trading_setups():

    print_status("Generating trading setups...")

    for symbol in tqdm(symbols, desc="Processing Symbols"):
        symbol_dir = get_symbol_directory(symbol)

        # Get list of all files in the download directory
        screenshot_files = glob(os.path.join(symbol_dir, "*.png"))
        if not screenshot_files:
            print_status(
                f"Warning: No screenshots found in download directory: {symbol_dir}"
            )
            continue

        if not openrouter_models:
            print_status(
                "No models found in OPENROUTER_MODELS. Skipping setup generation for this symbol."
            )
            continue

        with tqdm(
            total=len(openrouter_models),
            desc=f"Generating setups {symbol}",
            leave=False,
        ) as pbar:
            for model_name in openrouter_models:
                print_status(f"Generating setup for {symbol} using model: {model_name}")
                setup = get_openai_trading_setup(
                    openrouter_api_key,
                    openrouter_base_url,
                    model_name,
                    screenshot_files,
                )
                if setup:
                    save_trading_setup_to_file(symbol, setup, model_name)
                else:
                    print_status(
                        f"Failed to generate setup for {symbol} with model {model_name}"
                    )
                pbar.update(1)


def openai_message_content(screenshot_files):

    system_role = {"role": "system", "content": system_prompt}
    user_role = {"role": "user", "content": [{"type": "text", "text": user_prompt}]}

    # Add images to the user message content
    images_processed = 0
    for screenshot in screenshot_files:
        try:
            with open(screenshot, "rb") as file:
                base64_image = base64.b64encode(file.read()).decode("utf-8")
                user_role["content"].append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    }
                )
                images_processed += 1
        except Exception as e:
            print_status(f"Error processing image {screenshot}: {e}")
            continue

    if images_processed == 0:
        print_status("No valid images were processed. Cannot proceed with analysis.")
        return None

    messages = [system_role, user_role]

    return messages


def get_openai_trading_setup(openai_api_key, openai_base_url, model, screenshot_files):
    try:
        client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
        messages = openai_message_content(screenshot_files)

        response = client.chat.completions.create(model=model, messages=messages)

        return response.choices[0].message.content

    except Exception as e:
        print_status(f"Error: {e}")
        return None


# All LLMs are now processed via OpenRouter using the models specified in OPENROUTER_MODELS.
