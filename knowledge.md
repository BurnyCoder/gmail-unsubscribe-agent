# Gmail Unsubscribe Agent

## Project Overview
This project implements an agent that helps users unsubscribe from unwanted emails by finding messages with "unsubscribe" in them and extracting the unsubscribe links.

## Key Components
- `gmail_unsubscribe_agent.py`: Main agent implementation
- `cli.py`: Command-line interface
- `utils/http_utils.py`: Utility functions for HTTP requests

## Setup Requirements
1. Google Cloud Console project with Gmail API enabled
2. OAuth 2.0 credentials (Desktop application)
3. Python 3.6+
4. Required packages: google-api-python-client, google-auth-oauthlib, google-auth, requests

## Usage Flow
1. User authenticates with Gmail using OAuth2
2. Agent searches for emails containing "unsubscribe"
3. Agent extracts unsubscribe links from headers and body
4. User selects which emails to unsubscribe from
5. Agent provides unsubscribe links for manual action

## Security Considerations
- The agent does not automatically click unsubscribe links
- OAuth2 is used for secure authentication
- HTTP requests are made with proper error handling
