"""Google Calendar authentication module with simplified user flow."""
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging

logger = logging.getLogger(__name__)

class GoogleAuth:
    """Handles Google Calendar authentication with a simple user flow."""
    
    def __init__(self):
        """Initialize the auth handler."""
        self.creds = None
        self.token_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'token.pickle')
        self.credentials_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials.json')
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        
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
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(
                            f"credentials.json not found at {self.credentials_file}. Please place the credentials file in the project root directory."
                        )
                    
                    # This will open the browser for user login
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file,
                        self.scopes
                    )
                    self.creds = flow.run_local_server(
                        port=0,
                        prompt='consent',
                        success_message='Authentication successful! You can close this window.'
                    )
                    
                # Save the credentials for future use
                os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
                    
            return self.creds
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise 