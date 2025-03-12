from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from browser_use import Agent, BrowserConfig, Browser
import asyncio
from dotenv import load_dotenv
from browser_use import Controller, ActionResult
controller = Controller()

@controller.action('Ask user for information on what to do next')
def ask_human(question: str) -> str:
    answer = input(f'\n{question}\nInput: ')
    return ActionResult(extracted_content=answer)

load_dotenv()

prompt = """
Open gmail.com and go through the emails one by one.

For each, ask the user if they want to read it. If they want to read it, open the email and read it.
Ask the user if they want to draft a reply, if yes, draft a reply to the email.
Do not send any emails, just draft them.

Check calendar.google.com for availability before suggesting a time to meet.

Remember the choices.
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
        llm=ChatOpenAI(model='gpt-4o-mini'),
        
        controller=controller
    )
    result = await agent.run()
    print(result)


asyncio.run(main())
