# Gmail Unsubscribe Agent

This is an automated agent that helps you manage your Gmail inbox by either:
- Unsubscribing from unwanted emails (default functionality)
- Summarizing your most recent emails

The agent uses Chrome browser automation and LLM-powered browsing to navigate through Gmail.

## Prerequisites

- Python 3.11 or higher
- Chrome or Chromium browser
- API keys for Anthropic Claude (via Portkey)

## Setup

1. Make sure you have all dependencies installed:
   ```
   pip install -r requirements.txt
   ```

2. Copy the environment template to create your own `.env` file:
   ```
   cp .envtemplate .env
   ```

3. Edit the `.env` file to add your API keys:
   ```
   PORTKEY_API_BASE=your_portkey_api_base_here
   PORTKEY_API_KEY=your_portkey_api_key_here
   PORTKEY_VIRTUAL_KEY_ANTHROPIC=your_portkey_virtual_key_here
   # Optional: You can customize the agent's behavior by setting a custom prompt
   GMAIL_AGENT_PROMPT="Your custom prompt here"
   ```
   ```

## Running the Agent

There are two ways to run the agent:

### Option 1: Manual two-step process, good for first time

1. First, start Chrome with remote debugging enabled:
   ```
   ./start_chrome_gmail.sh
   ```
   This will open Chrome to Gmail. You may need to log in to your Gmail account.

2. Once Chrome is running with remote debugging, run the agent:
   ```
   python browser_gmail.py
   ```

### Option 2: Using the integrated script (after you're logged in)

Run the all-in-one script that handles both Chrome startup and the agent:

```
python run_gmail_agent.py
```

This script will:
- Start Chrome with remote debugging enabled
- Navigate to Gmail 
- Run the agent to process your emails
- Properly clean up when finished or interrupted

## Functionality

By default, the agent is configured to summarize your most recent email, providing:
- Sender information
- Subject line
- Date and time received
- A summary of the content

You can modify the agent's behavior by editing the `default_prompt` variable in either:
- `run_gmail_agent.py` (for the integrated script)
- `browser_gmail.py` (for the manual approach)

An alternative prompt for unsubscribing from emails is provided but commented out in both files.

## Stopping the Agent

- If using the integrated script: Press `Ctrl+C` in the terminal
- If using the manual approach: Press `Ctrl+C` in the terminal and manually close the Chrome window 