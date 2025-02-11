import base64
import os
import json

from glob import glob
from openai import OpenAI
from anthropic import Anthropic
from decouple import config
from tqdm import tqdm
from pprint import pprint

from llm_prompts import *
from helper_func import print_status, save_trading_setup_to_file, get_symbol_directory

symbols = json.loads(config("SYMBOLS"))

openai_model = config("OPENAI_MODEL")
openai_api_key = config("OPENAI_API_KEY")
openai_base_url = "https://api.openai.com/v1/"
deepseek_api_key = config("DEEPSEEK_API_KEY")
deepseek_model = config("DEEPSEEK_MODEL")
deepseek_base_url = "https://api.deepseek.com/"
gemini_api_key = config("GEMINI_API_KEY")
gemini_model = config("GEMINI_MODEL")
gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
openrouter_api_key = config("OPEN_ROUTER_API_KEY")
openrouter_model = config("OPEN_ROUTER_MODEL")
openrouter_base_url = "https://openrouter.ai/api/v1"
anthropic_model = config("ANTHROPIC_MODEL")
anthropic_api_key = config("ANTHROPIC_API_KEY")

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

        with tqdm(total=3, desc="Generating setups", leave=False) as pbar:
            chatgpt_setup = get_chatgpt_trading_setup(screenshot_files)
            save_trading_setup_to_file(symbol, chatgpt_setup, openai_model)
            pbar.update(1)

            gemini_setup = get_gemini_trading_setup(screenshot_files)
            save_trading_setup_to_file(symbol, gemini_setup, gemini_model)
            pbar.update(1)

            """
            anthropic_setup = get_anthropic_trading_setup(screenshot_files)
            save_trading_setup_to_file(symbol, anthropic_setup, anthropic_model)
            pbar.update(1)
            """

            openrouter_setup = get_openrouter_trading_setup(screenshot_files)
            save_trading_setup_to_file(symbol, openrouter_setup, openrouter_model)
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


def anthropic_message_content(screenshot_files):
    user_role = {"role": "user", "content": [{"type": "text", "text": user_prompt}]}

    # Add images to the user message content
    images_processed = 0
    for screenshot in screenshot_files:
        try:
            with open(screenshot, "rb") as file:
                base64_image = base64.b64encode(file.read()).decode("utf-8")
                user_role["content"].append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": f"{base64_image}",
                        },
                    }
                )
                images_processed += 1
        except Exception as e:
            print_status(f"Error processing image {screenshot}: {e}")
            continue

    if images_processed == 0:
        print_status("No valid images were processed. Cannot proceed with analysis.")
        return None

    messages = [user_role]

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


def get_anthropic_trading_setup(screenshot_files):
    try:
        client = Anthropic(api_key=anthropic_api_key)
        messages = anthropic_message_content(screenshot_files)

        response = client.messages.create(
            model=anthropic_model,
            messages=messages,
            max_tokens=4096,
            system=system_prompt,
        )

        return response.content[0].text

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


def get_openrouter_trading_setup(screenshot_files):
    return get_openai_trading_setup(
        openrouter_api_key,
        openrouter_base_url,
        openrouter_model,
        screenshot_files,
    )
