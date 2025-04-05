import streamlit as st
import imaplib
import json
import os
from pathlib import Path
import email
from tqdm import tqdm
from cryptography.fernet import Fernet
import base64

# Add this constant at the top of the file after imports
ENCRYPTION_KEY = b'YOUR_ENCRYPTION_KEY_HERE'  # Replace with a secure key
FERNET = Fernet(base64.urlsafe_b64encode(ENCRYPTION_KEY.ljust(32)[:32]))

def encrypt_data(data: str) -> str:
    """Encrypt a string using Fernet encryption"""
    return FERNET.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt a string using Fernet encryption"""
    return FERNET.decrypt(encrypted_data.encode()).decode()

def load_credentials():
    """Load and decrypt credentials from config file"""
    config_file = Path('mail_credentials.json')
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            encrypted_creds = json.load(f)
            
        # Decrypt credentials
        decrypted_creds = {key: decrypt_data(value) for key, value in encrypted_creds.items()}
        return decrypted_creds
    return None

def save_credentials(credentials):
    """Encrypt and save credentials to config file"""
    encrypted_creds = {key: encrypt_data(value) for key, value in credentials.items()}
    with open('mail_credentials.json', 'w') as f:
        json.dump(encrypted_creds, f)

def get_folder_stats(gmail):
    """Get statistics for Gmail folders"""
    folder_stats = []
    _, folders = gmail.list()
    
    for folder in folders:
        folder_name = folder.decode().split('"/"')[-1].strip('"')
        try:
            gmail.select(f'"{folder_name}"')
            _, messages = gmail.search(None, 'ALL')
            message_count = len(messages[0].split()) if messages[0] else 0
            folder_stats.append({"name": folder_name, "count": message_count})
        except:
            folder_stats.append({"name": folder_name, "count": "Unable to access"})
    
    return folder_stats

def main():
    st.title("Email Migration Tool")
    st.write("Migrate emails between email accounts")

    # Load existing credentials
    creds = load_credentials()

    # Credentials input form
    with st.form("credentials_form"):
        st.subheader("Email Credentials")
        
        gmail_email = st.text_input("Gmail Email", 
                                  value=creds.get('gmail_email', '') if creds else '')
        gmail_password = st.text_input("Gmail App Password", 
                                     value=creds.get('gmail_password', '') if creds else '',
                                     type="password")
        icloud_email = st.text_input("iCloud Email", 
                                   value=creds.get('icloud_email', '') if creds else '')
        icloud_password = st.text_input("iCloud App Password", 
                                      value=creds.get('icloud_password', '') if creds else '',
                                      type="password")
        
        submitted = st.form_submit_button("Save Credentials")
        
        if submitted:
            new_creds = {
                'gmail_email': gmail_email,
                'gmail_password': gmail_password,
                'icloud_email': icloud_email,
                'icloud_password': icloud_password
            }
            save_credentials(new_creds)
            st.success("Credentials saved successfully!")
            st.rerun()

    # Gmail folder analysis
    if st.button("Analyze Gmail Folders"):
        try:
            with st.spinner("Connecting to Gmail..."):
                gmail = imaplib.IMAP4_SSL('imap.gmail.com')
                gmail.login(gmail_email, gmail_password)
                
                folder_stats = get_folder_stats(gmail)
                
                st.subheader("Gmail Folders and Message Counts")
                for folder in folder_stats:
                    st.write(f"{folder['name']}: {folder['count']} messages")
                
                gmail.logout()
                
        except Exception as e:
            st.error(f"Error connecting to Gmail: {str(e)}")

    # Migration section (placeholder for future implementation)
    st.subheader("Migration")
    if st.button("Start Migration"):
        st.warning("Migration feature coming soon!")

if __name__ == "__main__":
    main()