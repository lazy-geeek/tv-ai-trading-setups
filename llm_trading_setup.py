import base64
import os
import json

from glob import glob
from openai import OpenAI
from decouple import config
from tqdm import tqdm
from pprint import pprint

from llm_prompts import *
from helper_func import print_status, save_trading_setup_to_file, get_symbol_directory

symbols = json.loads(config("SYMBOLS"))

openai_model = config("OPENAI_MODEL")
openai_api_key = config("OPENAI_API_KEY")
openai_base_url = "https://api.openai.com/v1/"

gemini_api_key = config("GEMINI_API_KEY")
gemini_model = config("GEMINI_MODEL")
gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

openrouter_api_key = config("OPENROUTER_API_KEY")
openrouter_base_url = "https://openrouter.ai/api/v1"

anthropic_model = config("ANTHROPIC_MODEL")

grok_model = config("GROK_MODEL")

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

        with tqdm(total=3, desc=f"Generating setups {symbol}", leave=False) as pbar:
            chatgpt_setup = get_chatgpt_trading_setup(screenshot_files)
            save_trading_setup_to_file(symbol, chatgpt_setup, openai_model)
            pbar.update(1)

            gemini_setup = get_gemini_trading_setup(screenshot_files)
            save_trading_setup_to_file(symbol, gemini_setup, gemini_model)
            pbar.update(1)

            anthropic_setup = get_openai_trading_setup(
                openrouter_api_key,
                openrouter_base_url,
                anthropic_model,
                screenshot_files,
            )
            save_trading_setup_to_file(symbol, anthropic_setup, anthropic_model)
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


def get_chatgpt_trading_setup(screenshot_files):
    return get_openai_trading_setup(
        openai_api_key, openai_base_url, openai_model, screenshot_files
    )


def get_gemini_trading_setup(screenshot_files):
    return get_openai_trading_setup(
        gemini_api_key, gemini_base_url, gemini_model, screenshot_files
    )
