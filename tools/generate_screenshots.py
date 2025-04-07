#!/usr/bin/env python3
"""Screenshot generation script for app store submissions."""
import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_directory(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)

def optimize_image(input_path):
    """Optimize PNG image for app store submission."""
    try:
        # Use optipng for PNG optimization
        subprocess.run(['optipng', '-o5', input_path], check=True)
        logger.info(f"Optimized {input_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to optimize {input_path}: {e}")
    except FileNotFoundError:
        logger.warning("optipng not found. Install with: sudo apt install optipng")

def take_screenshot(window_title, output_path, delay=2):
    """Take a screenshot of a specific window."""
    try:
        # Wait for the window to be ready
        time.sleep(delay)
        
        # Try to find the window ID
        wmctrl = subprocess.run(
            ['wmctrl', '-l'],
            capture_output=True,
            text=True,
            check=True
        )
        
        window_id = None
        for line in wmctrl.stdout.splitlines():
            if window_title in line:
                window_id = line.split()[0]
                break
        
        if not window_id:
            logger.error(f"Window '{window_title}' not found")
            return False
        
        # Activate the window
        subprocess.run(['wmctrl', '-i', '-a', window_id], check=True)
        time.sleep(1)  # Wait for window activation
        
        # Take screenshot with gnome-screenshot
        subprocess.run(
            ['gnome-screenshot', '-w', '-f', output_path],
            check=True
        )
        
        # Optimize the screenshot
        optimize_image(output_path)
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to take screenshot: {e}")
        return False
    except FileNotFoundError:
        logger.error("Required tools not found. Install with: sudo apt install wmctrl gnome-screenshot")
        return False

def main():
    """Main function."""
    # Ensure screenshots directory exists
    screenshots_dir = Path('screenshots')
    ensure_directory(screenshots_dir)
    
    # Create a test calendar event for the notification
    test_event = {
        'summary': 'Team Standup Meeting',
        'start': (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S'),
        'location': 'Online',
        'description': 'Daily team sync-up\n\nZoom Meeting Link: https://zoom.us/j/123456789'
    }
    
    # List of screenshots to take
    screenshots = [
        {
            'name': 'notification.png',
            'window': 'Meeting Notification',
            'delay': 3,
            'setup': lambda: subprocess.run(['fullscreen-meeting-notifier'])
        },
        {
            'name': 'settings.png',
            'window': 'Meeting Notifier Settings',
            'delay': 2,
            'setup': lambda: subprocess.run(['fullscreen-meeting-notifier', '--settings'])
        }
    ]
    
    try:
        for screenshot in screenshots:
            output_path = screenshots_dir / screenshot['name']
            logger.info(f"Taking screenshot: {screenshot['name']}")
            
            # Run the setup command
            process = screenshot['setup']()
            
            # Take the screenshot
            if take_screenshot(
                screenshot['window'],
                str(output_path),
                screenshot['delay']
            ):
                logger.info(f"Successfully captured {screenshot['name']}")
            else:
                logger.error(f"Failed to capture {screenshot['name']}")
            
            # Clean up
            subprocess.run(['pkill', 'fullscreen-meeting-notifier'])
            time.sleep(1)
        
        logger.info("Screenshots generated successfully!")
        logger.info(f"Screenshots saved in: {screenshots_dir.absolute()}")
        
    except Exception as e:
        logger.error(f"Error generating screenshots: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 