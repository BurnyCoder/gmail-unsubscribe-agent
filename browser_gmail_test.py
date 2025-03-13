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
Your task is to help the user summarize the most recent emails in Gmail.

1. Open gmail.com and log in if necessary
2. Identify the 2 most recent emails in the inbox
3. For each of these 2 emails:
   - Open the email
   - Extract the following information:
     a. Sender name and email address
     b. Subject line
     c. Date and time received
     d. Main content/body of the email (summarized)
   - Log a concise summary of each email
   - Close the email and move to the next one

Important instructions:
- Focus only on the 2 most recent emails
- Create clear, structured summaries that capture the key information
- Respect privacy by not sharing sensitive information
- Return to the Gmail inbox after summarizing each email
- Log each summary after completing it
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
    print(result.all_results[-1].extracted_content)
    return result.all_results[-1].extracted_content


if __name__ == "__main__":
    result = asyncio.run(main())
