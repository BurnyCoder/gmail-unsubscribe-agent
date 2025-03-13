# Gmail Unsubscribe Agent

This is an automated agent that helps you unsubscribe from unwanted emails in your Gmail inbox.

## Prerequisites

- Python 3.11 or higher
- Chrome browser
- API keys for the LLM (Anthropic Claude by default)

## Setup

1. Make sure you have all dependencies installed:
   ```
   pip install -r requirements.txt
   ```

2. Edit the `.env` file to add your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Running the Agent

1. First, start Chrome with remote debugging enabled:
   ```
   ./start_chrome.sh
   ```
   This will open Chrome to Gmail. You may need to log in to your Gmail account.

2. Once Chrome is running with remote debugging, run the unsubscribe agent:
   ```
   python browser_gmail.py
   ```

3. The agent will:
   - Navigate through your Gmail inbox
   - Look for unsubscribe links in emails
   - Click on them and complete the unsubscribe process
   - Log its progress in the terminal

## Customization

You can modify the `prompt` variable in `browser_gmail.py` to change the behavior of the agent.

## Stopping the Agent

To stop the agent, press `Ctrl+C` in the terminal where it's running. 