import os
import json

from tqdm import tqdm
from playwright.sync_api import sync_playwright
from decouple import config
from helper_func import (
    print_status,
    get_download_directory,
    get_symbol_directory,
    clear_download_directory,
)

endpoint_url = config("ENDPOINT_URL")
website_url = config("WEBSITE_URL")
chart_reload_timeout = int(config("CHART_RELOAD_TIMEOUT"))
timeframes = json.loads(config("TIMEFRAMES"))
symbols = json.loads(config("SYMBOLS"))

with sync_playwright() as p:
    print_status("Taking Tradingview screenshots...")

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

    # Loop through symbols with a progress bar
    for symbol in tqdm(symbols, desc="Processing Symbols"):
        download_directory = get_symbol_directory(symbol)

        page.keyboard.type(symbol)
        page.wait_for_timeout(chart_reload_timeout)
        page.keyboard.press("Enter")
        page.wait_for_timeout(chart_reload_timeout)

        # Loop through timeframes for the current symbol with a progress bar
        for timeframe in tqdm(timeframes, desc=f"Timeframes for {symbol}", leave=False):
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
            download.save_as(
                os.path.join(download_directory, download.suggested_filename)
            )

    # Close page
    page.close()

    print_status("Screenshots completed!")
