#!/usr/bin/env python3
"""
Example script demonstrating how to use the Gmail Unsubscribe Agent.
"""

from gmail.gmail_unsubscribe_agent import GmailUnsubscribeAgent

def main():
    # Initialize the agent
    agent = GmailUnsubscribeAgent(
        credentials_path="credentials.json",  # Path to your OAuth credentials
        token_path="token.json"               # Path to save the auth token
    )
    
    # Run the agent in interactive mode
    results = agent.run(
        max_emails=5,           # Process up to 5 emails
        auto_unsubscribe=False  # Ask before unsubscribing
    )
    
    # Print summary
    if results:
        print("\n--- Unsubscribe Summary ---")
        for item in results:
            email = item['email']
            result = item['result']
            
            print(f"Email: {email['subject']}")
            print(f"From: {email['sender']}")
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"Unsubscribe URL: {result['url']}")
            print()

if __name__ == "__main__":
    main()
