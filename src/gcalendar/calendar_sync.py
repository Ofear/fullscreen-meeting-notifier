"""Calendar sync module for fetching and monitoring Google Calendar events."""
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser
import pytz
import logging
import os

# Disable cache warnings
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

class CalendarSync:
    """Handles Google Calendar synchronization and event monitoring."""
    
    def __init__(self, credentials):
        """Initialize the calendar service with credentials."""
        # Disable cache file
        os.environ['GOOGLE_DISCOVERY_SERVICE_ACCOUNT_CACHE'] = 'false'
        
        self.service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        self.timezone = pytz.timezone('UTC')  # Default to UTC
        try:
            # Try to get user's timezone from calendar settings
            settings = self.service.settings().get(setting='timezone').execute()
            if settings.get('value'):
                self.timezone = pytz.timezone(settings['value'])
        except Exception as e:
            logger.warning(f"Could not get user timezone, using UTC: {e}")
        
    def get_upcoming_events(self, minutes_ahead=5):
        """Get upcoming events starting in the next few minutes or hours.
        
        Args:
            minutes_ahead (int): Number of minutes to look ahead for events.
                               Default is 5 minutes for immediate notifications.
                               Use larger values like 1440 (24 hours) for daily view.
        """
        try:
            now = datetime.now(self.timezone)
            time_min = now.isoformat()
            time_max = (now + timedelta(minutes=minutes_ahead)).isoformat()
            
            # For longer time ranges, increase the max results
            max_results = 50 if minutes_ahead > 60 else 10
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                maxResults=max_results
            ).execute()
            
            events = events_result.get('items', [])
            upcoming = []
            
            for event in events:
                # Get event start time
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_time = parser.parse(start)
                
                # Make sure start_time is timezone aware
                if start_time.tzinfo is None:
                    start_time = self.timezone.localize(start_time)
                
                # For immediate notifications (5 minutes), only include events about to start
                # For longer ranges (daily view), include all events in the range
                if minutes_ahead <= 5:
                    if not (start_time > now and start_time <= now + timedelta(minutes=minutes_ahead)):
                        continue
                
                # Extract meeting link from conference data
                meeting_link = None
                if 'conferenceData' in event:
                    for entry in event.get('conferenceData', {}).get('entryPoints', []):
                        if entry.get('entryPointType') == 'video':
                            meeting_link = entry.get('uri')
                            break
                
                upcoming.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start_time': start_time,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'meeting_link': meeting_link,
                    'attendees': [
                        attendee.get('email')
                        for attendee in event.get('attendees', [])
                        if attendee.get('email')
                    ],
                    'organizer': event.get('organizer', {}).get('email', '')
                })
            
            # Sort events by start time
            upcoming.sort(key=lambda x: x['start_time'])
            return upcoming
            
        except HttpError as error:
            logger.error(f"Failed to fetch calendar events: {error}")
            if error.resp.status == 401:
                # Handle authentication errors
                raise Exception("Calendar access unauthorized. Please sign in again.")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching calendar events: {e}")
            raise 