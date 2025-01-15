from playwright.sync_api import sync_playwright

endpoint_url = "http://localhost:9222"
website_url = "https://tradingview.com/chart/vmxrGQjo/"

with sync_playwright() as p:

    # TODO Set download directory

    # Connect to the existing browser instance
    browser = p.chromium.connect_over_cdp(endpoint_url)

    # Get the default browser context (this will use the existing user profile)
    context = browser.contexts[0]

    # Create a new page in the existing context
    page = context.new_page()

    # Navigate to a website (it should already be logged in)
    page.goto(website_url)

    # TODO Loop through watchlist symbols

    # TODO Go to 5m timeframe

    page.wait_for_timeout(5000)
    page.keyboard.press("Control+Alt+S")

    # TODO Go to 15m timeframe

    # TODO Press Auto adjust chart
    page.wait_for_timeout(5000)
    page.keyboard.press("Control+Alt+S")

    # TODO Go to 1h timeframe

    page.wait_for_timeout(5000)
    page.keyboard.press("Control+Alt+S")

    # TODO Go to 4h timeframe

    page.wait_for_timeout(5000)
    page.keyboard.press("Control+Alt+S")

    # TODO Get Symbol Name from downloaded screenshot

    # TODO Loop through LLMs (OpenAI, Claude, Deepseek)

    # TODO Send downloaded screenshots to LLM for trading setup

    # TODO Send generated trading setups to LLM for evaluation and consolidation

    # TODO If all LLMs give similar trading setup, add setup to mail body

    # TODO When watchlist symbol loop has finished,
    # Phase 1 -> Save to text file on computer
    # Phase 2 -> Send email

# TODO Function for Download Keypress
