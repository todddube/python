import imaplib
import json
import os
from pathlib import Path
import getpass
import email
from tqdm import tqdm

def load_credentials():
    """Load credentials from config file or prompt user"""
    config_file = Path('mail_credentials.json')
    
    # Create dummy credentials if file doesn't exist
    if not config_file.exists():
        dummy_creds = {
            'gmail_email': 'your.email@gmail.com',
            'gmail_password': 'your-gmail-app-password',
            'icloud_email': 'your.email@icloud.com', 
            'icloud_password': 'your-icloud-app-password'
        }
        with open(config_file, 'w') as f:
            json.dump(dummy_creds, f)
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    
    credentials = {
        'gmail_email': input("Enter Gmail email: "),
        'gmail_password': getpass.getpass("Enter Gmail app password: "),
        'icloud_email': input("Enter iCloud email: "),
        'icloud_password': getpass.getpass("Enter iCloud app password: ")
    }
    
    # Save credentials
    with open(config_file, 'w') as f:
        json.dump(credentials, f)
    
    return credentials

def migrate_emails():
    # Load credentials
    creds = load_credentials()
    # Connect to Gmail
    gmail = imaplib.IMAP4_SSL('imap.gmail.com')
    gmail.login(creds['gmail_email'], creds['gmail_password'])
    
    try:
        # List all folders/labels
        _, folders = gmail.list()
        
        print("\nGmail Folders and Message Counts:")
        print("-" * 40)
        
        for folder in folders:
            # Parse folder name
            folder_name = folder.decode().split('"/"')[-1].strip('"')
            
            try:
                # Select folder and count messages
                gmail.select(f'"{folder_name}"')
                _, messages = gmail.search(None, 'ALL')
                message_count = len(messages[0].split()) if messages[0] else 0
                
                print(f"{folder_name}: {message_count} messages")
            except:
                print(f"{folder_name}: Unable to access")
                
    finally:
        # Cleanup
        gmail.logout()

if __name__ == "__main__":
    try:
        print("Starting email migration...")
        migrate_emails()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {str(e)}")