import shutil
import os
import base64
import json


from playwright.sync_api import sync_playwright
from openai import OpenAI
from decouple import config
from pprint import pprint

endpoint_url = config("ENDPOINT_URL")
website_url = config("WEBSITE_URL")
download_directory = config("DOWNLOAD_DIRECTORY")
chart_reload_timeout = int(config("CHART_RELOAD_TIMEOUT"))
timeframes = json.loads(config("TIMEFRAMES"))
symbols = json.loads(config("SYMBOLS"))
openai_api_key = config("OPENAI_API_KEY")
openai_base_url = "https://api.openai.com/v1/"
deepseek_api_key = config("DEEPSEEK_API_KEY")
deepseek_base_url = "https://api.deepseek.ai/v1/"
anthropic_api_key = config("ANTHROPIC_API_KEY")


def clear_download_directory():
    # Delete all files from download directory
    for filename in os.listdir(download_directory):
        file_path = os.path.join(download_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


def get_trading_setup(openai_api_key, openai_base_url, model):

    system_prompt = config("TRADING_SYSTEM_PROMPT")
    user_prompt = config("TRADING_USER_PROMPT")

    try:

        client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)

        system_message_content = [{"type": "text", "text": system_prompt}]
        user_message_content = [{"type": "text", "text": user_prompt}]

        # Add each file to the message content
        for screenshot in download_directory:
            with open(screenshot, "rb") as file:
                file_content = base64.b64encode(file.read()).decode("utf-8")
                user_message_content.append({"type": "file", "data": file_content})

        response = client.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message_content},
                {"role": "user", "content": user_message_content},
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return None


with sync_playwright() as p:

    # Delete all files from download directory
    clear_download_directory()

    # Connect to the existing browser instance
    browser = p.chromium.connect_over_cdp(endpoint_url)

    # Get the default browser context (this will use the existing user profile)
    context = browser.contexts[0]

    # Create a new page in the existing context
    page = context.new_page()
    page.set_default_timeout(10000)

    # Navigate to a website (it should already be logged in)
    page.goto(website_url)

    # Loop through symbols

    for symbol in symbols:

        page.keyboard.type(symbol)
        page.wait_for_timeout(chart_reload_timeout)
        page.keyboard.press("Enter")
        page.wait_for_timeout(chart_reload_timeout)

        # Loop through timeframes
        for timeframe in timeframes:

            # Change timeframe by typing
            page.keyboard.type(timeframe)
            page.wait_for_timeout(chart_reload_timeout)
            page.keyboard.press("Enter")
            page.wait_for_timeout(chart_reload_timeout)

            # Download screenshot
            with page.expect_download() as download_info:
                page.keyboard.press("Control+Alt+S")

            download = download_info.value

            # Wait for the download process to complete and save the downloaded file in specified path
            download.save_as(download_directory + "/" + download.suggested_filename)

        # Loop through LLMs (OpenAI, Claude, Deepseek)

        openai_setup = get_trading_setup(openai_api_key, openai_base_url, "gpt-4o")
        pprint(openai_setup)

    # TODO Send downloaded screenshots to LLM for trading setup

    # TODO Send generated trading setups to LLM for evaluation and consolidation

    # TODO If all LLMs give similar trading setup, add setup to mail body

    # TODO When watchlist symbol loop has finished,
    # Phase 1 -> Save to text file on computer
    # Phase 2 -> Send email

# TODO Function for Download Keypress
