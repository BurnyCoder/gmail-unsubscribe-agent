import requests
from urllib.parse import urlparse

def is_valid_url(url):
    """
    Check if a URL is valid.
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def safe_get_request(url, timeout=10):
    """
    Make a safe GET request to a URL.
    
    Args:
        url (str): URL to request
        timeout (int): Request timeout in seconds
        
    Returns:
        tuple: (success, response_or_error)
    """
    if not is_valid_url(url):
        return False, "Invalid URL"
    
    try:
        response = requests.get(url, timeout=timeout)
        return True, response
    except requests.exceptions.RequestException as e:
        return False, str(e)

def safe_post_request(url, data=None, json=None, timeout=10):
    """
    Make a safe POST request to a URL.
    
    Args:
        url (str): URL to request
        data (dict): Form data to send
        json (dict): JSON data to send
        timeout (int): Request timeout in seconds
        
    Returns:
        tuple: (success, response_or_error)
    """
    if not is_valid_url(url):
        return False, "Invalid URL"
    
    try:
        response = requests.post(url, data=data, json=json, timeout=timeout)
        return True, response
    except requests.exceptions.RequestException as e:
        return False, str(e)
