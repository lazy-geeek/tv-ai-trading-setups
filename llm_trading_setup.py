import base64
import os
import json

from glob import glob
from openai import OpenAI
from anthropic import Anthropic
from decouple import config
from pprint import pprint

from llm_prompts import *
from helper_func import print_status, save_trading_setup_to_file

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
anthropic_model = config("ANTHROPIC_MODEL")
anthropic_api_key = config("ANTHROPIC_API_KEY")

system_prompt = TRADING_SYSTEM_PROMPT
user_prompt = TRADING_USER_PROMPT


def generate_trading_setups():
    for symbol in symbols:
        base_dir = config("DOWNLOAD_DIRECTORY")
        symbol_dir = os.path.join(base_dir, symbol)

        # Validate download directory exists
        if not os.path.exists(symbol_dir):
            print(f"Error: Download directory does not exist: {symbol_dir}")
            continue

        # Get list of all files in the download directory
        screenshot_files = glob(os.path.join(symbol_dir, "*.png"))
        if not screenshot_files:
            print(f"Warning: No screenshots found in download directory: {symbol_dir}")
            continue

        print_status("Get ChatGPT trading setup...")
        chatgpt_setup = get_chatgpt_trading_setup(screenshot_files)
        save_trading_setup_to_file(symbol, chatgpt_setup, "chatgpt")

        print_status("Get Gemini trading setup...")
        gemini_setup = get_gemini_trading_setup(screenshot_files)
        save_trading_setup_to_file(symbol, gemini_setup, "gemini")

        print_status("Get Anthropic trading setup...")
        anthropic_setup = get_anthropic_trading_setup(screenshot_files)
        save_trading_setup_to_file(symbol, anthropic_setup, "claude")

        print_status("Get Deepseek trading setup...")
        deepseek_setup = get_deepseek_trading_setup(screenshot_files)
        save_trading_setup_to_file(symbol, deepseek_setup, "deepseek")


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
            print(f"Error processing image {screenshot}: {e}")
            continue

    if images_processed == 0:
        print("No valid images were processed. Cannot proceed with analysis.")
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
            print(f"Error processing image {screenshot}: {e}")
            continue

    if images_processed == 0:
        print("No valid images were processed. Cannot proceed with analysis.")
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
        print(f"Error: {e}")
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
        print(f"Error: {e}")
        return None


def get_chatgpt_trading_setup(screenshot_files):
    return get_openai_trading_setup(
        openai_api_key, openai_base_url, openai_model, screenshot_files
    )


def deepseek_message_content(screenshot_files):
    # Deepseek expects a simpler message format
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Add images to the user message
    images_processed = 0
    image_content = ""
    for screenshot in screenshot_files:
        try:
            with open(screenshot, "rb") as file:
                base64_image = base64.b64encode(file.read()).decode("utf-8")
                image_content += f"\n<image>{base64_image}</image>"
                images_processed += 1
        except Exception as e:
            print(f"Error processing image {screenshot}: {e}")
            continue

    if images_processed == 0:
        print("No valid images were processed. Cannot proceed with analysis.")
        return None

    # Append images to the user message
    messages[1]["content"] += image_content
    return messages


def get_deepseek_trading_setup(screenshot_files):
    try:
        client = OpenAI(api_key=deepseek_api_key, base_url=deepseek_base_url)
        messages = deepseek_message_content(screenshot_files)

        if messages is None:
            return None

        response = client.chat.completions.create(
            model=deepseek_model, messages=messages
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_gemini_trading_setup(screenshot_files):
    return get_openai_trading_setup(
        gemini_api_key, gemini_base_url, gemini_model, screenshot_files
    )
