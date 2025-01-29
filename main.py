from llm_trading_setup import *
from helper_func import print_status

print_status("Get ChatGPT trading setup...")
chatgpt_setup = get_chatgpt_trading_setup()

print_status("Get Deepseek trading setup...")
deepseek_setup = get_openai_trading_setup()

print_status("Get Gemini trading setup...")
gemini_setup = get_openai_trading_setup()

print_status("Get Anthropic trading setup...")
anthropic_setup = get_anthropic_trading_setup(anthropic_api_key, anthropic_model)
