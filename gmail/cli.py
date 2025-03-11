import argparse
import sys
import os
from gmail.gmail_unsubscribe_agent import GmailUnsubscribeAgent

def main():
    """Main entry point for the Gmail Unsubscribe Agent CLI."""
    parser = argparse.ArgumentParser(
        description="Gmail Unsubscribe Agent - Automatically unsubscribe from unwanted emails"
    )
    
    parser.add_argument(
        "--credentials", 
        default="credentials.json",
        help="Path to the Google API credentials.json file"
    )
    
    parser.add_argument(
        "--token", 
        default="token.json",
        help="Path to save the authentication token"
    )
    
    parser.add_argument(
        "--max", 
        type=int, 
        default=10,
        help="Maximum number of emails to process"
    )
    
    parser.add_argument(
        "--auto", 
        action="store_true",
        help="Automatically unsubscribe without prompting"
    )
    
    args = parser.parse_args()
    
    # Check if credentials file exists
    if not os.path.exists(args.credentials):
        print(f"Error: Credentials file not found at {args.credentials}")
        print("Please download your credentials.json file from the Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select an existing one")
        print("3. Enable the Gmail API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download the credentials.json file")
        return 1
    
    # Initialize and run the agent
    try:
        agent = GmailUnsubscribeAgent(
            credentials_path=args.credentials,
            token_path=args.token
        )
        
        results = agent.run(
            max_emails=args.max,
            auto_unsubscribe=args.auto
        )
        
        # Print summary
        if results:
            print("\n--- Unsubscribe Summary ---")
            success_count = sum(1 for r in results if r['result']['success'])
            print(f"Processed: {len(results)} emails")
            print(f"Successful unsubscribe links found: {success_count}")
        
        return 0
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
