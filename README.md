# Gmail Unsubscribe Agent

A simple agent that helps you unsubscribe from unwanted emails by finding messages with "unsubscribe" in them and extracting the unsubscribe links.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/gmail-unsubscribe.git
cd gmail-unsubscribe

# Install the package
pip install -e .
```

## Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials.json file and save it in your working directory

## Usage

```bash
# Basic usage
gmail-unsubscribe

# Specify custom credentials file
gmail-unsubscribe --credentials /path/to/credentials.json

# Process more emails
gmail-unsubscribe --max 20

# Automatically unsubscribe without prompting
gmail-unsubscribe --auto
```

## How it works

The Gmail Unsubscribe Agent:

1. Authenticates with your Gmail account using OAuth2
2. Searches for emails containing "unsubscribe"
3. Extracts unsubscribe links from:
   - List-Unsubscribe headers
   - Email body content
4. Presents the emails and allows you to choose which ones to unsubscribe from
5. Provides the unsubscribe links for you to visit

## Security Note

This agent only extracts unsubscribe links and does not automatically click them for security reasons. You will need to manually visit the links to complete the unsubscription process.
