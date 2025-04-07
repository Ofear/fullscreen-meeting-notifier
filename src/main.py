#!/usr/bin/env python3
"""FullScreen Meeting Notifier main application."""
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk, GLib, Notify, AyatanaAppIndicator3 as AppIndicator, Gdk
import signal
import sys
from datetime import datetime
import logging
import os
import json
import pytz
import webbrowser
from .version import VERSION
from .update_checker import UpdateChecker

# Change to the script's directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

from auth.google_auth import GoogleAuth
from gcalendar.calendar_sync import CalendarSync
from ui.notification_window import NotificationWindow
from ui.settings_window import SettingsWindow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MeetingNotifier:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        # Initialize notifications
        Notify.init("Meeting Notifier")
        
        self.auth = GoogleAuth()
        try:
            credentials = self.auth.authenticate()
            self.calendar = CalendarSync(credentials)
        except Exception as e:
            logger.error(f"Failed to authenticate: {e}")
            sys.exit(1)
            
        self.active_notifications = {}
        self.dismissed_events = set()  # Track dismissed event IDs
        self.settings_window = None
        
        # Initialize update checker
        self.update_checker = UpdateChecker()
        
        # Load settings
        self.settings_file = os.path.expanduser('~/.config/meeting-notifier/settings.json')
        self.dismissed_events_file = os.path.expanduser('~/.config/meeting-notifier/dismissed_events.json')
        self.load_settings()
        self.load_dismissed_events()
        
        # Create today's meetings window
        self.create_meetings_window()
        
        # Create app indicator
        self.indicator = AppIndicator.Indicator.new(
            "meeting-notifier",
            "appointment-soon",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        
        # Create menu
        self.create_indicator_menu()
        
        # Check for updates on startup
        GLib.timeout_add_seconds(5, self.check_updates)
        # Schedule periodic update checks (daily)
        GLib.timeout_add_seconds(24 * 60 * 60, self.check_updates)
        
        # Start checking for meetings every minute
        GLib.timeout_add_seconds(60, self.check_meetings)
        # Do initial check
        self.check_meetings()
        
        # Show meetings window on startup if launched from applications menu
        if os.environ.get('DESKTOP_STARTUP_ID'):
            self.show_meetings_window()

    def load_settings(self):
        """Load settings from file."""
        self.settings = {
            'background_color': 'rgba(0, 0, 0, 0.9)',
            'background_image': '',
            'notification_sound': '/usr/share/sounds/freedesktop/stereo/message.oga',  # Default system notification sound
            'sound_enabled': True,  # Enable sound by default
            'text_color': '#ffffff',
            'button_color': '#4a4a4a',
            'button_text_color': '#ffffff',
            'opacity': 0.85
        }
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings.update(json.load(f))
        except Exception as e:
            logger.error(f"Error loading settings: {e}")

    def load_dismissed_events(self):
        """Load dismissed events from file."""
        try:
            if os.path.exists(self.dismissed_events_file):
                with open(self.dismissed_events_file, 'r') as f:
                    data = json.load(f)
                    # Filter out events older than 24 hours
                    current_time = datetime.now().timestamp()
                    self.dismissed_events = set(
                        event_id for event_id, timestamp in data.items()
                        if current_time - timestamp < 24 * 3600  # 24 hours in seconds
                    )
        except Exception as e:
            logger.error(f"Error loading dismissed events: {e}")
            self.dismissed_events = set()

    def save_dismissed_events(self):
        """Save dismissed events to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.dismissed_events_file), exist_ok=True)
            # Save events with current timestamp
            current_time = datetime.now().timestamp()
            data = {event_id: current_time for event_id in self.dismissed_events}
            with open(self.dismissed_events_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving dismissed events: {e}")

    def create_meetings_window(self):
        """Create the window to display today's meetings."""
        self.meetings_window = Gtk.Window(title="Meeting Notifier")
        self.meetings_window.set_default_size(400, 300)
        self.meetings_window.set_resizable(True)  # Enable window resizing
        self.meetings_window.connect("delete-event", self.on_window_delete)
        self.meetings_window.set_icon_name("appointment-soon")
        
        # Create header bar
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title("Meeting Notifier")
        header_bar.set_decoration_layout("menu:minimize,maximize,close")
        self.meetings_window.set_titlebar(header_bar)
        
        # Set up CSS styling for content only
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(b"""
            headerbar {
                background: linear-gradient(to bottom, #2c3e50, #2c3e50);
                border: none;
                color: white;
                min-height: 36px;
            }
            headerbar button.titlebutton {
                min-height: 20px;
                min-width: 20px;
                padding: 3px;
                margin: 0 2px;
                border: none;
                box-shadow: none;
                opacity: 1;
                -gtk-icon-shadow: none;
            }
            headerbar button.titlebutton.close {
                background-image: -gtk-icontheme("window-close-symbolic");
                background-repeat: no-repeat;
                background-position: center;
                background-size: 14px;
                color: white;
                opacity: 0.8;
            }
            headerbar button.titlebutton.close:hover {
                background-color: #e74c3c;
                opacity: 1;
            }
            headerbar button.titlebutton.maximize {
                background-image: -gtk-icontheme("window-maximize-symbolic");
                background-repeat: no-repeat;
                background-position: center;
                background-size: 14px;
                color: white;
                opacity: 0.8;
            }
            headerbar button.titlebutton.minimize {
                background-image: -gtk-icontheme("window-minimize-symbolic");
                background-repeat: no-repeat;
                background-position: center;
                background-size: 14px;
                color: white;
                opacity: 0.8;
            }
            headerbar button.titlebutton:hover {
                background-color: rgba(255,255,255,0.1);
                opacity: 1;
            }
            window decoration {
                margin: 0;
                border: none;
            }
            .main-content {
                background-color: #ffffff;
                padding: 15px;
                border-radius: 6px;
            }
            .header-label {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .meeting-title {
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
            }
            .meeting-time {
                color: #34495e;
                font-size: 13px;
            }
            .status-label {
                color: #7f8c8d;
                font-size: 12px;
                margin-top: 5px;
            }
            .meetings-list {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 4px;
            }
            .meetings-list row {
                background-color: #ffffff;
                border-bottom: 1px solid #ecf0f1;
                padding: 10px;
                transition: all 0.2s ease;
            }
            .meetings-list row:hover {
                background-color: #f8f9fa;
            }
            button {
                background: linear-gradient(to bottom, #3498db, #2980b9);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.2);
                transition: all 0.2s ease;
            }
            button:hover {
                background: linear-gradient(to bottom, #3cb0fd, #3498db);
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            button.join-meeting {
                background: linear-gradient(to bottom, #3498db, #2980b9);
                color: white;
                padding: 6px 12px;
                margin: 5px;
                font-size: 13px;
            }
            button.join-meeting:hover {
                background: linear-gradient(to bottom, #3cb0fd, #3498db);
            }
            scrolledwindow {
                border: none;
                background: transparent;
            }
            scrolledwindow undershoot, 
            scrolledwindow overshoot {
                background: none;
            }
            scrollbar {
                background-color: transparent;
                border: none;
            }
            scrollbar slider {
                min-width: 6px;
                min-height: 6px;
                border-radius: 3px;
                background-color: #bdc3c7;
            }
            scrollbar slider:hover {
                background-color: #95a5a6;
            }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Create main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.get_style_context().add_class('main-content')
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        main_box.set_vexpand(True)  # Allow vertical expansion
        main_box.set_hexpand(True)  # Allow horizontal expansion
        
        # Add header label
        header = Gtk.Label()
        header.get_style_context().add_class('header-label')
        header.set_markup("Today's Meetings")
        main_box.pack_start(header, False, False, 0)
        
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)  # Allow both horizontal and vertical scrolling
        scrolled.set_vexpand(True)  # Allow vertical expansion
        scrolled.set_hexpand(True)  # Allow horizontal expansion
        
        # Create list box for meetings
        self.meetings_list = Gtk.ListBox()
        self.meetings_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.meetings_list.get_style_context().add_class('meetings-list')
        self.meetings_list.set_vexpand(True)  # Allow vertical expansion
        self.meetings_list.set_hexpand(True)  # Allow horizontal expansion
        
        scrolled.add(self.meetings_list)
        main_box.pack_start(scrolled, True, True, 0)
        
        # Add status label
        self.status_label = Gtk.Label()
        self.status_label.get_style_context().add_class('status-label')
        self.status_label.set_markup("Checking for meetings every minute")
        main_box.pack_start(self.status_label, False, False, 0)
        
        self.meetings_window.add(main_box)
        
    def create_indicator_menu(self):
        """Create the indicator menu."""
        menu = Gtk.Menu()
        
        # Show Meetings item
        show_item = Gtk.MenuItem(label="Show Meetings")
        show_item.connect("activate", lambda _: self.show_meetings_window())
        menu.append(show_item)
        
        # Settings item
        settings_item = Gtk.MenuItem(label="Settings")
        settings_item.connect("activate", self.show_settings)
        menu.append(settings_item)
        
        # Check Now item
        check_item = Gtk.MenuItem(label="Check Now")
        check_item.connect("activate", self.check_meetings)
        menu.append(check_item)
        
        # Check for Updates item
        update_item = Gtk.MenuItem(label="Check for Updates")
        update_item.connect("activate", lambda _: self.check_updates(force=True))
        menu.append(update_item)
        
        # Version info item
        version_item = Gtk.MenuItem(label=f"Version: {VERSION}")
        version_item.set_sensitive(False)  # Make it non-clickable
        menu.append(version_item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        # Quit item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit_application)
        menu.append(quit_item)
        
        menu.show_all()
        self.indicator.set_menu(menu)
        
    def show_meetings_window(self):
        """Show and update the meetings window."""
        self.update_meetings_list()
        self.meetings_window.show_all()
        self.meetings_window.present()
        
    def update_meetings_list(self):
        """Update the list of today's meetings."""
        # Remove existing items
        for child in self.meetings_list.get_children():
            self.meetings_list.remove(child)
            
        try:
            # Get today's meetings (24 hours ahead)
            events = self.calendar.get_upcoming_events(minutes_ahead=1440)  # 24 hours
            
            if not events:
                # Show "No meetings today" message
                row = Gtk.ListBoxRow()
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                box.set_margin_top(10)
                box.set_margin_bottom(10)
                box.set_margin_start(10)
                box.set_margin_end(10)
                
                label = Gtk.Label()
                label.get_style_context().add_class('meeting-title')
                label.set_markup("No meetings today")
                box.pack_start(label, True, True, 0)
                
                row.add(box)
                self.meetings_list.add(row)
            else:
                # Add each meeting to the list
                for event in events:
                    row = Gtk.ListBoxRow()
                    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                    box.set_margin_top(10)
                    box.set_margin_bottom(10)
                    box.set_margin_start(10)
                    box.set_margin_end(10)
                    
                    # Meeting title
                    title = Gtk.Label()
                    title.get_style_context().add_class('meeting-title')
                    title.set_markup(event['summary'])
                    title.set_halign(Gtk.Align.START)
                    box.pack_start(title, True, True, 0)
                    
                    # Meeting time
                    time_str = event['start_time'].strftime("%I:%M %p")
                    time_label = Gtk.Label()
                    time_label.get_style_context().add_class('meeting-time')
                    time_label.set_markup(f"Time: {time_str}")
                    time_label.set_halign(Gtk.Align.START)
                    box.pack_start(time_label, True, True, 0)
                    
                    # Meeting link if available
                    if event.get('meeting_link'):
                        link_button = Gtk.LinkButton.new_with_label(
                            event['meeting_link'],
                            "Join Meeting"
                        )
                        link_button.get_style_context().add_class('join-meeting')
                        link_button.set_halign(Gtk.Align.START)
                        box.pack_start(link_button, True, True, 0)
                    
                    row.add(box)
                    self.meetings_list.add(row)
            
            self.meetings_list.show_all()
            
            # Update last checked time
            now = datetime.now().strftime("%I:%M %p")
            self.status_label.set_markup(f"Last checked: {now}")
            
        except Exception as e:
            logger.error(f"Failed to update meetings list: {e}")
            self.status_label.set_markup("Failed to fetch meetings")
        
    def on_window_delete(self, window, event):
        """Handle window close."""
        window.hide()
        return True
        
    def check_meetings(self, *args):
        """Check for upcoming meetings and show notifications."""
        try:
            upcoming = self.calendar.get_upcoming_events()
            for event in upcoming:
                event_id = event['id']
                # Skip if event was dismissed or if notification is already active
                if event_id in self.dismissed_events or event_id in self.active_notifications:
                    continue
                notification = NotificationWindow(event, is_primary=True)
                self.active_notifications[event_id] = notification
                
                def on_notification_closed(window, event_id=event_id):
                    """Handle notification window closure."""
                    if event_id in self.active_notifications:
                        del self.active_notifications[event_id]
                        # Add to dismissed events when explicitly dismissed
                        if hasattr(window, 'was_dismissed') and window.was_dismissed:
                            self.dismissed_events.add(event_id)
                            self.save_dismissed_events()  # Save to disk when dismissing
                
                notification.connect("destroy", on_notification_closed)
                notification.show_all()
            
            # Update meetings window if it exists and is visible
            if hasattr(self, 'meetings_window') and self.meetings_window.get_visible():
                self.update_meetings_list()
            
            return True  # Continue checking
        except Exception as e:
            logger.error(f"Error checking meetings: {e}")
            return True  # Continue checking despite error
        
    def show_settings(self, _):
        """Show the settings window."""
        if self.settings_window is None:
            self.settings_window = SettingsWindow(parent_settings=self.settings)
            self.settings_window.connect("destroy", self.on_settings_closed)
        self.settings_window.present()
    
    def on_settings_closed(self, window):
        """Handle settings window closure."""
        self.settings_window = None
        # Reload settings
        self.load_settings()
        
    def quit_application(self, *args):
        """Quit the application."""
        Notify.uninit()
        Gtk.main_quit()
        
    def check_updates(self, *args, force=False):
        """Check for application updates."""
        if force:
            # Reset last check time to force an update check
            if os.path.exists(self.update_checker.last_check_file):
                os.remove(self.update_checker.last_check_file)
        
        update_info = self.update_checker.check_for_updates()
        if update_info:
            has_update, latest_version, changelog_url = update_info
            if has_update:
                self.show_update_notification(latest_version, changelog_url)
        
        return True  # Continue periodic checks
    
    def show_update_notification(self, latest_version, changelog_url):
        """Show a notification about available updates."""
        dialog = Gtk.MessageDialog(
            transient_for=self.meetings_window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text="Update Available"
        )
        
        dialog.format_secondary_text(
            f"A new version ({latest_version}) of Meeting Notifier is available.\n"
            "Would you like to view the release notes?"
        )
        
        # Add custom buttons
        dialog.add_button("Remind Me Later", Gtk.ResponseType.CANCEL)
        dialog.add_button("View Release Notes", Gtk.ResponseType.OK)
        
        # Make the dialog window float above others
        dialog.set_keep_above(True)
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            # Open changelog in default browser
            webbrowser.open(changelog_url)

def main():
    """Main application entry point."""
    try:
        # Set up signal handling
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
        
        # Create and initialize the application
        app = MeetingNotifier()
        
        # Run the GTK main loop
        print("Starting GTK main loop...")
        Gtk.main()
        
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
        Gtk.main_quit()
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("Cleaning up...")
        Notify.uninit()

if __name__ == "__main__":
    main()