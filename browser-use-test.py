from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from tasks import cdp_task

import asyncio
from decouple import config


browserConfig = BrowserConfig(
    chrome_instance_path="C:/Program Files/Google/Chrome/Application"
    # cdp_url="http://127.0.0.1:9222"
)

browser = Browser(browserConfig)


user = config("TV_USERNAME")
password = config("TV_PASSWORD")

task = cdp_task


# llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
llm = ChatOpenAI(model_name="gpt-4o")


async def main():
    agent = Agent(llm=llm, task=task, browser=browser)
    result = await agent.run()
    print(result)


asyncio.run(main())
