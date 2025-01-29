import base64
import os
from glob import glob
from openai import OpenAI
from anthropic import Anthropic
from decouple import config
from pprint import pprint

download_directory = config("DOWNLOAD_DIRECTORY")

# Validate download directory exists
if not os.path.exists(download_directory):
    print(f"Error: Download directory does not exist: {download_directory}")
    screenshot_files = []
else:
    # Get list of all files in the download directory
    screenshot_files = glob(os.path.join(download_directory, "*"))
    if not screenshot_files:
        print(f"Warning: No files found in download directory: {download_directory}")
openai_model = config("OPENAI_MODEL")
openai_api_key = config("OPENAI_API_KEY")
openai_base_url = "https://api.openai.com/v1/"
deepseek_api_key = config("DEEPSEEK_API_KEY")
deepseek_model = config("DEEPSEEK_MODEL")
deepseek_base_url = "https://api.deepseek.ai/v1/"
gemini_api_key = config("GEMINI_API_KEY")
gemini_model = config("GEMINI_MODEL")
gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
anthropic_model = config("ANTHROPIC_MODEL")
anthropic_api_key = config("ANTHROPIC_API_KEY")


def openai_message_content():
    system_prompt = config("TRADING_SYSTEM_PROMPT")
    user_prompt = config("TRADING_USER_PROMPT")

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


def anthropic_message_content():
    user_prompt = config("TRADING_USER_PROMPT")

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


def get_openai_trading_setup(openai_api_key, openai_base_url, model):

    try:

        client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)

        messages = openai_message_content()

        response = client.chat.completions.create(model=model, messages=messages)

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_anthropic_trading_setup():

    system_prompt = config("TRADING_SYSTEM_PROMPT")

    try:
        client = Anthropic(api_key=anthropic_api_key)

        messages = anthropic_message_content()

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


def get_chatgpt_trading_setup():
    return get_openai_trading_setup(openai_api_key, openai_base_url, openai_model)


def get_deepseek_trading_setup():
    return get_openai_trading_setup(deepseek_api_key, deepseek_base_url, deepseek_model)


def get_gemini_trading_setup():
    return get_openai_trading_setup(gemini_api_key, gemini_base_url, gemini_model)
