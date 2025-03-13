from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL
import os

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

# Get Portkey configuration from environment variables
PORTKEY_API_BASE = os.getenv("PORTKEY_API_BASE")
PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
PORTKEY_VIRTUAL_KEY_ANTHROPIC = os.getenv("PORTKEY_VIRTUAL_KEY_ANTHROPIC")


async def main(prompt: str):
    # Set up Portkey headers for Anthropic/Claude
    portkey_headers = createHeaders(
        api_key=PORTKEY_API_KEY, 
        provider="anthropic",
        virtual_key=PORTKEY_VIRTUAL_KEY_ANTHROPIC
    )
    
    # Create LLM with Portkey configuration using Claude
    llm = ChatAnthropic(
        model="claude-3-7-sonnet-latest",
        api_key=PORTKEY_VIRTUAL_KEY_ANTHROPIC,  # Using the virtual key as the API key
        base_url=PORTKEY_API_BASE,  # Using the custom API base
        default_headers=portkey_headers
    )
    
    agent = Agent(
        browser=Browser(
            config=BrowserConfig(
                disable_security=True,
                cdp_url="http://localhost:9222",
            ),
        ),
        task=prompt,
        llm=llm,  # Use the Portkey-configured Claude LLM
        controller=controller
    )
    result = await agent.run()
    # Access the final result's extracted_content which contains the email summaries
    final_answer = result.final_result()
    print(final_answer)
    return final_answer


if __name__ == "__main__":
    default_prompt = """
    Your task is to help the user summarize the most recent email in Gmail.

    1. Open gmail.com and log in if necessary
    2. Identify the most recent email in the inbox
    3. For this email:
       - Open the email
       - Extract the following information:
         a. Sender name and email address
         b. Subject line
         c. Date and time received
         d. Main content/body of the email (summarized)
       - Log a concise summary of the email
       - Close the email

    Important instructions:
    - Focus only on the most recent email
    - Create clear, structured summaries that capture the key information
    - Respect privacy by not sharing sensitive information
    - Return to the Gmail inbox after summarizing the email
    - Log the summary after completing it
    """
    
#     default_prompt = """
# Your task is to help the user unsubscribe from unwanted emails in Gmail.

# 1. Open gmail.com and log in if necessary
# 2. Go through the emails in the inbox one by one
# 3. For each email:
#    - Open the email
#    - Look for an "unsubscribe" link somewhere in the email (usually at the bottom)
#    - If an unsubscribe link is found:
#      a. Click on the unsubscribe link
#      b. Complete any unsubscribe process - this might open a new tab or show a dialog
#      c. If it opens a new tab, confirm the unsubscription on that website or page
#      d. Close any new tabs opened during the process and return to Gmail
#      e. Log the name of the sender you've unsubscribed from
#    - If no unsubscribe link is found, just close the email and move to the next one
# 4. Continue this process for all visible emails in the inbox

# Important instructions:
# - Be thorough in finding unsubscribe links - they might be labeled as "manage subscriptions" or similar
# - Look for unsubscribe text in small font at the bottom of emails
# - After unsubscribing, make sure to come back to the Gmail inbox
# - Keep track of which senders you've unsubscribed from
# """
    result = asyncio.run(main(default_prompt))
