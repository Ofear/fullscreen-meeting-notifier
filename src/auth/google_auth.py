"""Google Calendar authentication module with simplified user flow."""
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class GoogleAuth:
    """Handles Google Calendar authentication with a simple user flow."""
    
    def __init__(self):
        """Initialize the auth handler."""
        self.creds = None
        self.config_dir = Path.home() / '.config' / 'meeting-notifier'
        self.token_file = str(self.config_dir / 'token.pickle')
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Load OAuth config from a secure location
        config_file = os.path.join(os.path.dirname(__file__), 'oauth_config.json')
        try:
            with open(config_file, 'r') as f:
                self.client_config = json.load(f)
        except FileNotFoundError:
            # Use embedded config for AppImage distribution
            self.client_config = {
                "installed": {
                    "client_id": "YOUR_CLIENT_ID",
                    "project_id": "YOUR_PROJECT_ID",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "YOUR_CLIENT_SECRET",
                    "redirect_uris": ["http://localhost"]
                }
            }
        
    def authenticate(self):
        """
        Authenticate with Google Calendar.
        Opens a browser window for user login if needed.
        """
        try:
            # Try to load existing credentials
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
                    
            # If no valid credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # Use embedded credentials
                    flow = InstalledAppFlow.from_client_config(
                        self.client_config,
                        self.scopes,
                        redirect_uri='http://localhost'
                    )
                    self.creds = flow.run_local_server(
                        port=0,
                        prompt='consent',
                        success_message='Authentication successful! You can close this window.'
                    )
                    
                # Save the credentials for future use
                self.config_dir.mkdir(parents=True, exist_ok=True)
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
                    
            return self.creds
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise 