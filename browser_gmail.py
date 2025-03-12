from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from browser_use import Agent, BrowserConfig, Browser
import asyncio
from dotenv import load_dotenv
from browser_use import Controller, ActionResult
controller = Controller()

# We can remove the ask_human action since we won't be asking for confirmation
# But we'll keep a logging action to track progress

@controller.action('Log progress')
def log_progress(message: str) -> str:
    """Log the progress of the unsubscribe process"""
    print(f"\n[LOG] {message}")
    return ActionResult(extracted_content="Logged successfully")

load_dotenv()

prompt = """
Your task is to help the user unsubscribe from unwanted emails in Gmail.

1. Open gmail.com and log in if necessary
2. Go through the emails in the inbox one by one
3. For each email:
   - Open the email
   - Look for an "unsubscribe" link somewhere in the email (usually at the bottom)
   - If an unsubscribe link is found:
     a. Click on the unsubscribe link
     b. Complete any unsubscribe process - this might open a new tab or show a dialog
     c. If it opens a new tab, confirm the unsubscription on that website or page
     d. Close any new tabs opened during the process and return to Gmail
     e. Log the name of the sender you've unsubscribed from
   - If no unsubscribe link is found, just close the email and move to the next one
4. Continue this process for all visible emails in the inbox

Important instructions:
- Be thorough in finding unsubscribe links - they might be labeled as "manage subscriptions" or similar
- Look for unsubscribe text in small font at the bottom of emails
- After unsubscribing, make sure to come back to the Gmail inbox
- Keep track of which senders you've unsubscribed from
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
