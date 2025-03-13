from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from browser_use import Agent, BrowserConfig, Browser
import asyncio
from dotenv import load_dotenv
from browser_use import Controller, ActionResult
controller = Controller()

load_dotenv()

prompt = """
Your task is to find cats on wikipedia and tell me which one is the cutest.
"""

async def main():
    agent = Agent(
        browser=Browser(
            config=BrowserConfig(
                disable_security=True,
                cdp_url="http://localhost:9222",
            ),
        ),
        task=prompt,
        llm=ChatAnthropic(model='claude-3-7-sonnet-latest'),
        controller=controller
    )
    result = await agent.run()
    print(result)


asyncio.run(main())
