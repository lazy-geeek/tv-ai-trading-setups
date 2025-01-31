from openai import OpenAI
from decouple import config

openai_model = config("OPENAI_MODEL")
openai_api_key = config("OPENAI_API_KEY")


def summarize_trading_setups(setups: list[str]) -> str:

    # Your OpenAI-compatible API configuration
    client = OpenAI(api_key=openai_api_key)

    # Construct the prompt
    messages = [
        {
            "role": "system",
            "content": """You're a professional trading analyst. Compare these trading setups and identify:
            1. Key similarities in entry/exit rules, indicators, and risk management
            2. Main differences between the setups
            3. Final conclusion if they represent similar approaches
            Use clear, concise bullet points.""",
        },
        {
            "role": "user",
            "content": f"Compare these 4 trading setups:\n\nSetup 1: {setup1}\n\nSetup 2: {setup2}\n\nSetup 3: {setup3}\n\nSetup 4: {setup4}",
        },
    ]

    # Send to LLM
    response = client.chat.completions.create(
        model=openai_model,
        messages=messages,
        temperature=0.3,  # Lower temperature for more factual analysis
        max_tokens=1000,
    )

    print(response.choices[0].message.content)
