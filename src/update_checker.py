"""Update checker for the application."""
import requests
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from .version import VERSION, get_version

logger = logging.getLogger(__name__)

class UpdateChecker:
    """Checks for application updates."""
    
    def __init__(self):
        """Initialize the update checker."""
        self.config_dir = Path.home() / '.config' / 'meeting-notifier'
        self.last_check_file = self.config_dir / 'last_update_check.json'
        self.check_interval = timedelta(days=7)  # Check weekly
        
    def should_check(self):
        """Determine if it's time to check for updates."""
        if not self.last_check_file.exists():
            return True
            
        try:
            with open(self.last_check_file) as f:
                data = json.load(f)
                last_check = datetime.fromisoformat(data['last_check'])
                return datetime.now() - last_check >= self.check_interval
        except Exception as e:
            logger.error(f"Error reading last update check: {e}")
            return True
            
    def save_last_check(self):
        """Save the timestamp of the last update check."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.last_check_file, 'w') as f:
                json.dump({
                    'last_check': datetime.now().isoformat(),
                    'current_version': VERSION
                }, f)
        except Exception as e:
            logger.error(f"Error saving update check: {e}")
            
    def check_for_updates(self):
        """Check for available updates.
        
        Returns:
            tuple: (has_update, latest_version, changelog_url) or None if check fails
        """
        if not self.should_check():
            return None
            
        try:
            # Replace with your actual update check URL
            response = requests.get(
                'https://api.github.com/repos/yourusername/fullscreen-meeting-notifier/releases/latest',
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            latest_version = data['tag_name'].lstrip('v')
            changelog_url = data['html_url']
            
            has_update = latest_version > VERSION
            self.save_last_check()
            
            return (has_update, latest_version, changelog_url)
            
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None 