#!/usr/bin/env python3
import os
import subprocess
import time
import sys
import signal
import asyncio
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL
from browser_use import Agent, BrowserConfig, Browser, Controller, ActionResult
from dotenv import load_dotenv

# Create a controller for actions
controller = Controller()

@controller.action('Log progress')
def log_progress(message: str) -> str:
    """Log the progress of the unsubscribe process"""
    print(f"\n[LOG] {message}")
    return ActionResult(extracted_content="Logged successfully")

# Load environment variables
load_dotenv()

# Get Portkey configuration from environment variables
PORTKEY_API_BASE = os.getenv("PORTKEY_API_BASE")
PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
PORTKEY_VIRTUAL_KEY_ANTHROPIC = os.getenv("PORTKEY_VIRTUAL_KEY_ANTHROPIC")

chrome_process = None

def start_chrome():
    """Start Chrome with remote debugging enabled"""
    global chrome_process
    
    # Close any existing Chrome instances with the debug profile
    try:
        subprocess.run(
            "pkill -f \"chrome.*--remote-debugging-port=9222\"", 
            shell=True, 
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass  # Ignore errors if no matching process found
    
    # Determine which Chrome binary to use
    chrome_bin = None
    for binary in ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]:
        try:
            if subprocess.run(["which", binary], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
                chrome_bin = binary
                break
        except Exception:
            continue
    
    if not chrome_bin:
        print("Error: Chrome or Chromium browser not found")
        sys.exit(1)
    
    print(f"Starting {chrome_bin} with remote debugging...")
    
    # Start Chrome with remote debugging
    chrome_process = subprocess.Popen(
        [
            chrome_bin,
            "--remote-debugging-port=9222",
            "--user-data-dir=/tmp/chrome-debug-profile",
            "https://gmail.com"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Give Chrome time to start and fully load
    print("Waiting for Chrome to start...")
    time.sleep(5)

async def run_agent(prompt: str):
    """Run the unsubscribe agent with the given prompt"""
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

def cleanup(signum=None, frame=None):
    """Cleanup function to kill Chrome when the script exits"""
    global chrome_process
    if chrome_process:
        print("Shutting down Chrome...")
        chrome_process.terminate()
        try:
            chrome_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            chrome_process.kill()
    sys.exit(0)

def main():
    """Main function to run the entire process"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # Start Chrome with remote debugging
        start_chrome()
        
        # Default prompt for the agent
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
        
        # Run the agent
        asyncio.run(run_agent(default_prompt))
    
    finally:
        # Ensure Chrome is shut down properly
        cleanup()

if __name__ == "__main__":
    main() 