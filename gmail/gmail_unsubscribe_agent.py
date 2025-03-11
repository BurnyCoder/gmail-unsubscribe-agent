import os
import base64
import re
import json
from email.mime.text import MIMEText
from urllib.parse import urlparse, parse_qs

try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    print("Required packages not installed. Please run: pip install google-api-python-client google-auth-oauthlib google-auth")
    exit(1)

class GmailUnsubscribeAgent:
    """
    An agent that finds emails with 'unsubscribe' in them and helps unsubscribe from them.
    """
    
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        """
        Initialize the Gmail Unsubscribe Agent.
        
        Args:
            credentials_path (str): Path to the credentials.json file from Google Cloud Console
            token_path (str): Path to save the token.json file for authentication
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        
        # Check if token.json exists with stored credentials
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_info(
                json.loads(open(self.token_path).read()), self.SCOPES)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Build the Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def find_unsubscribe_emails(self, max_results=50):
        """
        Find emails containing 'unsubscribe' in them.
        
        Args:
            max_results (int): Maximum number of emails to retrieve
            
        Returns:
            list: List of message objects containing unsubscribe links
        """
        if not self.service:
            self.authenticate()
        
        # Search for emails containing 'unsubscribe'
        query = "unsubscribe"
        results = self.service.users().messages().list(
            userId='me', q=query, maxResults=max_results).execute()
        
        messages = results.get('messages', [])
        unsubscribe_emails = []
        
        for message in messages:
            msg = self.service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            
            # Extract email details
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            
            # Look for unsubscribe link in headers (List-Unsubscribe header)
            list_unsubscribe = next((h['value'] for h in headers if h['name'] == 'List-Unsubscribe'), None)
            
            # Also look for unsubscribe links in the email body
            body_links = self.extract_unsubscribe_links_from_body(msg)
            
            if list_unsubscribe or body_links:
                unsubscribe_emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'header_unsubscribe': list_unsubscribe,
                    'body_unsubscribe_links': body_links
                })
        
        return unsubscribe_emails
    
    def extract_unsubscribe_links_from_body(self, message):
        """
        Extract unsubscribe links from email body.
        
        Args:
            message (dict): Gmail API message object
            
        Returns:
            list: List of unsubscribe URLs found in the email body
        """
        links = []
        
        # Check if the message has parts (multipart email)
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data:
                        decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                        # Find URLs containing 'unsubscribe' using regex
                        urls = re.findall(r'href=[\'"]?([^\'" >]+)[\'"]?', decoded_data)
                        for url in urls:
                            if 'unsubscribe' in url.lower():
                                links.append(url)
        # Check if the message has a body directly
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            data = message['payload']['body']['data']
            decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
            # Find URLs containing 'unsubscribe' using regex
            urls = re.findall(r'href=[\'"]?([^\'" >]+)[\'"]?', decoded_data)
            for url in urls:
                if 'unsubscribe' in url.lower():
                    links.append(url)
        
        return links
    
    def unsubscribe(self, email_info):
        """
        Attempt to unsubscribe from an email.
        
        Args:
            email_info (dict): Email information containing unsubscribe links
            
        Returns:
            dict: Result of unsubscribe attempt
        """
        # First try the List-Unsubscribe header if available
        if email_info.get('header_unsubscribe'):
            unsubscribe_url = self._extract_url_from_header(email_info['header_unsubscribe'])
            if unsubscribe_url:
                print(f"Unsubscribing from {email_info['sender']} using header link...")
                # Here you would implement the actual HTTP request to the unsubscribe URL
                # For safety, we're just returning the URL for manual handling
                return {
                    'success': True,
                    'method': 'header',
                    'url': unsubscribe_url,
                    'message': f"Please visit this URL to unsubscribe: {unsubscribe_url}"
                }
        
        # If no header or header unsubscribe failed, try body links
        if email_info.get('body_unsubscribe_links'):
            print(f"Unsubscribing from {email_info['sender']} using body link...")
            unsubscribe_url = email_info['body_unsubscribe_links'][0]
            return {
                'success': True,
                'method': 'body',
                'url': unsubscribe_url,
                'message': f"Please visit this URL to unsubscribe: {unsubscribe_url}"
            }
        
        return {
            'success': False,
            'message': f"Could not find a valid unsubscribe link for {email_info['sender']}"
        }
    
    def _extract_url_from_header(self, header_value):
        """
        Extract URL from List-Unsubscribe header.
        
        Args:
            header_value (str): List-Unsubscribe header value
            
        Returns:
            str: Extracted URL or None
        """
        # List-Unsubscribe can contain mailto: or http(s): URLs
        # We prefer http(s) links for automated unsubscribing
        urls = re.findall(r'<(https?:[^>]+)>', header_value)
        if urls:
            return urls[0]
        
        # If no http link, check for mailto
        mailto = re.findall(r'<mailto:([^>]+)>', header_value)
        if mailto:
            # For mailto links, we would need to send an email
            # This is more complex and not implemented here
            return None
        
        return None
    
    def run(self, max_emails=10, auto_unsubscribe=False):
        """
        Run the unsubscribe agent.
        
        Args:
            max_emails (int): Maximum number of emails to process
            auto_unsubscribe (bool): Whether to automatically unsubscribe
            
        Returns:
            list: Results of unsubscribe attempts
        """
        print(f"Finding emails with 'unsubscribe' (max: {max_emails})...")
        unsubscribe_emails = self.find_unsubscribe_emails(max_results=max_emails)
        
        if not unsubscribe_emails:
            print("No emails with unsubscribe links found.")
            return []
        
        print(f"Found {len(unsubscribe_emails)} emails with unsubscribe links.")
        
        results = []
        for i, email in enumerate(unsubscribe_emails):
            print(f"\n{i+1}. Subject: {email['subject']}")
            print(f"   From: {email['sender']}")
            
            if auto_unsubscribe:
                result = self.unsubscribe(email)
                results.append({
                    'email': email,
                    'result': result
                })
            else:
                # Interactive mode
                choice = input("Unsubscribe from this email? (y/n/q): ").lower()
                if choice == 'q':
                    break
                elif choice == 'y':
                    result = self.unsubscribe(email)
                    results.append({
                        'email': email,
                        'result': result
                    })
                    print(result['message'])
        
        return results
