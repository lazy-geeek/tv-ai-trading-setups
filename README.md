# AI Trading Setups Analysis

Automated trading setup analysis using browser automation and multiple LLM providers.

## Features
- Automated TradingView screenshot capture across multiple timeframes
- Multi-model analysis (OpenAI, Gemini, Anthropic via OpenRouter)
- Automated Excel report generation with risk/reward metrics
- Configurable symbols and timeframes
- Progress tracking with tqdm
- Cross-platform browser automation with Playwright

## Tech Stack
- Python 3.10+
- Playwright 1.39+
- Poetry 1.6+
- OpenAI API
- Google Gemini API
- Anthropic Claude (via OpenRouter)
- OpenPyXL (Excel reporting)

## Installation
```bash
# Install Python dependencies
poetry install

# Install Playwright browsers
playwright install
```

## Configuration
Create `.env` file with these settings:
```ini
ENDPOINT_URL="[Browser WS Endpoint]"
WEBSITE_URL="[TradingView URL]"
TF_RELOAD_TIMEOUT=2000
CHART_RELOAD_TIMEOUT=5000
TIMEFRAMES='["1D", "4H", "1H"]'  # Supported timeframes
SYMBOLS='["EURUSD", "GBPUSD", "XAUUSD"]'  # Symbols to analyze
DOWNLOAD_DIRECTORY="downloads"

# API Configuration
OPENAI_MODEL="gpt-4-vision-preview"
OPENAI_API_KEY="sk-..."
GEMINI_MODEL="gemini-pro-vision"
GEMINI_API_KEY="..."
OPENROUTER_API_KEY="..."
ANTHROPIC_MODEL="claude-3-opus"
SUMMARY_MODEL="gpt-3.5-turbo"
```

## Usage
```bash
python main_new.py
```

### Process Flow
1. Clears previous download directory
2. Connects to existing browser instance via Playwright
3. For each symbol:
   - Captures screenshots across configured timeframes
   - Generates analyses from 3 AI models (OpenAI/Gemini/Anthropic)
   - Creates summary Excel report with key metrics:
     - Entry/Exit prices
     - Risk-reward ratios
     - Stop Loss/Take Profit levels
     - Pips calculations

## File Structure
```
tv-ai-trading-setups/
├── main_new.py             # Main execution script
├── helper_func.py          # Directory management utilities
├── llm_prompts.py          # AI prompt templates
├── playwright_tradingview.py # Browser automation helpers
└── poetry.lock             # Dependency lock file
```

## Requirements
- Active TradingView subscription (for chart access)
- API keys for LLM providers
- Chrome browser installed
