import shutil
import os
import json

from playwright.sync_api import sync_playwright
from decouple import config

endpoint_url = config("ENDPOINT_URL")
website_url = config("WEBSITE_URL")
download_directory = config("DOWNLOAD_DIRECTORY")
chart_reload_timeout = int(config("CHART_RELOAD_TIMEOUT"))
timeframes = json.loads(config("TIMEFRAMES"))
symbols = json.loads(config("SYMBOLS"))


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

        download_directory = download_directory + "/" + symbol + "/"

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
            download.save_as(download_directory + download.suggested_filename)
