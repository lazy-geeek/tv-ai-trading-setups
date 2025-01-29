import base64
import os
from glob import glob
from io import BytesIO
from PIL import Image

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
openai_api_key = config("OPENAI_API_KEY")
openai_base_url = "https://api.openai.com/v1/"
deepseek_api_key = config("DEEPSEEK_API_KEY")
deepseek_base_url = "https://api.deepseek.ai/v1/"
anthropic_api_key = config("ANTHROPIC_API_KEY")


def resize_image(image_path, max_size=800):
    """Resize image while maintaining aspect ratio."""
    with Image.open(image_path) as img:
        # Convert to RGB if needed
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Calculate new dimensions maintaining aspect ratio
        ratio = max_size / max(img.size)
        if ratio < 1:  # Only resize if image is larger than max_size
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Save to bytes
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        return buffer.getvalue()


def get_openai_trading_setup(openai_api_key, openai_base_url, model):

    system_prompt = config("TRADING_SYSTEM_PROMPT")
    user_prompt = config("TRADING_USER_PROMPT")

    try:

        client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)

        # Prepare the messages with proper format for vision model
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [{"type": "text", "text": user_prompt}]},
        ]

        # Add images to the user message content
        images_processed = 0
        for screenshot in screenshot_files:
            try:
                with open(screenshot, "rb") as file:
                    base64_image = base64.b64encode(file.read()).decode("utf-8")
                    messages[1]["content"].append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
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

        response = client.chat.completions.create(
            model=model, messages=messages, max_tokens=1000
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_anthropic_trading_setup(anthropic_api_key, model):
    system_prompt = config("TRADING_SYSTEM_PROMPT")
    user_prompt = config("TRADING_USER_PROMPT")

    try:
        client = Anthropic(api_key=anthropic_api_key)

        # Prepare the message content with system prompt and user prompt
        message_content = f"{system_prompt}\n\nHuman: {user_prompt}"

        # Add resized images to the message content
        images_processed = 0
        for screenshot in screenshot_files:
            try:
                # Resize image and convert to base64
                image_data = resize_image(screenshot)
                base64_image = base64.b64encode(image_data).decode("utf-8")
                message_content += f"\n<image>{base64_image}</image>"
                images_processed += 1
            except Exception as e:
                print(f"Error processing image {screenshot}: {e}")
                continue

        if images_processed == 0:
            print("No valid images were processed. Cannot proceed with analysis.")
            return None

        message_content += "\n\nAssistant: Let me analyze these trading setups for you."

        response = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": message_content,
                }
            ],
        )

        return response.content[0].text

    except Exception as e:
        print(f"Error: {e}")
        return None


# Loop through LLMs (OpenAI, Claude, Deepseek)

openai_setup = get_openai_trading_setup(openai_api_key, openai_base_url, "gpt-4o")
pprint(openai_setup)

anthropic_setup = get_anthropic_trading_setup(
    anthropic_api_key, "claude-3-opus-20240229"
)
pprint(anthropic_setup)
