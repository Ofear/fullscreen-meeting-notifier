"""Full-screen notification window module."""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Pango
import html
import re
import os
import json

class NotificationWindow(Gtk.Window):
    """Full-screen notification window that appears on all monitors."""
    
    def __init__(self, event_data, is_primary=True, primary_window=None):
        """Initialize the notification window."""
        print(f"Initializing {'primary' if is_primary else 'secondary'} notification window...")
        print(f"Event data: {event_data}")
        try:
            super().__init__(title="Meeting Notification")
            self.event_data = event_data
            self.is_primary = is_primary
            self.primary_window = primary_window
            self.windows = [self] if is_primary else (primary_window.windows if primary_window else [])
            self.was_dismissed = False  # Track if window was explicitly dismissed
            
            # Load settings
            self.settings_file = os.path.expanduser('~/.config/meeting-notifier/settings.json')
            print(f"Loading settings from {self.settings_file}")
            self.load_settings()
            print(f"Settings loaded: {self.settings}")
            
            # Set window properties
            print("Setting window properties...")
            self.set_app_paintable(True)
            self.set_visual(self.get_screen().get_rgba_visual())
            self.set_decorated(False)
            self.set_keep_above(True)
            self.set_skip_taskbar_hint(True)
            self.set_skip_pager_hint(True)
            
            # Make window semi-transparent
            self.set_opacity(self.settings.get('opacity', 0.85))
            
            # Connect draw signal for background image
            self.connect("draw", self.on_draw)
            
            # Create the content for this window
            print("Creating window content...")
            self.create_window_content()
            
            # Only create additional windows if this is the primary window
            if self.is_primary:
                print("Creating monitor windows...")
                self.create_monitor_windows()
                
                # Play notification sound if enabled
                if self.settings.get('sound_enabled', True):
                    print("Playing notification sound...")
                    self.play_notification_sound()
            
            print(f"{'Primary' if is_primary else 'Secondary'} window initialization complete.")
            
        except Exception as e:
            print(f"Error initializing notification window: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def position_window(self):
        """Position the window on the screen."""
        # Remove this method as positioning is now handled in create_monitor_windows
        return False
    
    def load_settings(self):
        """Load settings from file."""
        self.settings = {
            'background_color': 'rgba(0, 0, 0, 0.9)',
            'background_image': '',
            'notification_sound': '/usr/share/sounds/freedesktop/stereo/message.oga',
            'sound_enabled': True,
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
            print(f"Error loading settings: {e}")
    
    def play_notification_sound(self):
        """Play the notification sound."""
        if self.settings.get('sound_enabled', True):  # Only play if sound is enabled
            sound_file = self.settings.get('notification_sound')
            if sound_file and os.path.exists(sound_file):
                os.system(f'ffplay -nodisp -autoexit -loglevel quiet -af "volume=0.75" "{sound_file}" &')  # Run in background
    
    def create_window_content(self):
        """Create the content for a notification window."""
        # Create main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0.9))
        self.add(self.main_box)
        
        # Create scrollable content area
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_box.pack_start(scrolled_window, True, True, 0)
        
        # Content box inside scrolled window
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_margin_top(50)
        content_box.set_margin_bottom(50)
        content_box.set_margin_start(50)
        content_box.set_margin_end(50)
        content_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0.7))
        scrolled_window.add(content_box)
        
        # Add meeting information
        title_label = Gtk.Label()
        title_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
        title_label.set_text(self.event_data['summary'])
        content_box.pack_start(title_label, False, False, 10)
        
        time_str = self.event_data['start_time'].strftime("%I:%M %p")
        time_label = Gtk.Label()
        time_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
        time_label.set_text(f"Starting now: {time_str}")
        content_box.pack_start(time_label, False, False, 5)
        
        # Extract and display meeting URL if present
        zoom_urls = []
        if self.event_data.get('description'):
            # Look for Zoom URL in the description
            zoom_urls = re.findall(r'https://[\w.-]+/j/\d+(?:\?[^\s\n]*)?', self.event_data['description'])
            if zoom_urls:
                url_label = Gtk.Label()
                url_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.4, 0.7, 1, 1))
                url_label.set_markup(f'<a href="{zoom_urls[0]}">{zoom_urls[0]}</a>')
                url_label.set_use_markup(True)
                url_label.set_track_visited_links(False)
                content_box.pack_start(url_label, False, False, 10)
            
            # Display the rest of the description
            desc_label = Gtk.Label()
            desc_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
            desc_label.set_text(self.event_data['description'])
            desc_label.set_line_wrap(True)
            desc_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            desc_label.set_justify(Gtk.Justification.LEFT)
            desc_label.set_halign(Gtk.Align.START)
            content_box.pack_start(desc_label, False, False, 5)
        
        # Add fixed button box at the bottom
        button_box = Gtk.Box(spacing=15)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.08, 0.08, 0.08, 0.95))
        button_box.set_margin_top(10)
        button_box.set_margin_bottom(10)
        
        # Add Join Meeting button if URL is present
        if zoom_urls:
            join_btn = Gtk.Button.new_with_label("Join Meeting")
            join_btn.get_style_context().add_class("suggested-action")  # Makes it stand out
            join_btn.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
            join_btn.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.6, 0.9, 1))
            join_btn.connect("clicked", self.on_join_clicked, zoom_urls[0])
            button_box.pack_start(join_btn, False, False, 0)
        
        dismiss_btn = Gtk.Button.new_with_label("Dismiss")
        dismiss_btn.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
        dismiss_btn.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.6, 0.2, 0.2, 1))
        dismiss_btn.connect("clicked", self.on_dismiss_clicked)
        button_box.pack_start(dismiss_btn, False, False, 0)
        
        snooze_btn = Gtk.Button.new_with_label("Snooze (5 min)")
        snooze_btn.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
        snooze_btn.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.4, 0.4, 0.4, 1))
        snooze_btn.connect("clicked", self.on_snooze_clicked)
        button_box.pack_start(snooze_btn, False, False, 0)
        
        self.main_box.pack_end(button_box, False, False, 0)
    
    def format_description(self, description):
        """Format HTML description into Pango markup."""
        # Escape special characters
        text = html.escape(description)
        
        # Replace HTML line breaks with newlines
        text = re.sub(r'<br\s*/?>|</br>', '\n', text)
        
        # Handle paragraphs
        text = re.sub(r'</p>\s*<p>', '\n\n', text)
        text = re.sub(r'</?p>', '', text)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove other HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Convert URLs to clickable links
        text = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', text)
        
        # Trim extra whitespace
        text = text.strip()
        
        return f'<span color="white">{text}</span>'
    
    def create_monitor_windows(self):
        """Create a window for each monitor."""
        display = Gdk.Display.get_default()
        n_monitors = display.get_n_monitors()
        print(f"Creating windows for {n_monitors} monitors")
        
        # If there's only one monitor, just position the primary window
        if n_monitors <= 1:
            monitor = display.get_monitor(0)
            geometry = monitor.get_geometry()
            self.move(geometry.x, geometry.y)
            self.fullscreen()
            self.show_all()
            return
            
        # For multiple monitors, create a window for each one
        # First, position the primary window on the primary monitor
        primary_monitor = display.get_primary_monitor()
        if primary_monitor:
            print("Using primary monitor for primary window")
            geometry = primary_monitor.get_geometry()
            self.move(geometry.x, geometry.y)
            self.fullscreen()
            self.show_all()
            
            # Create windows for non-primary monitors
            for i in range(n_monitors):
                monitor = display.get_monitor(i)
                if monitor == primary_monitor:
                    print(f"Skipping monitor {i} (primary)")
                    continue  # Skip primary monitor as it's already handled
                    
                print(f"Creating secondary window for monitor {i}")
                # Create secondary window with reference to primary
                window = NotificationWindow(self.event_data, is_primary=False, primary_window=self)
                geometry = monitor.get_geometry()
                window.move(geometry.x, geometry.y)
                window.fullscreen()
                window.show_all()
                self.windows.append(window)
                window.connect("destroy", self.on_window_destroyed)
        else:
            print("No primary monitor found, using first monitor")
            # Fallback if no primary monitor is set
            # Use the first monitor for primary window
            geometry = display.get_monitor(0).get_geometry()
            self.move(geometry.x, geometry.y)
            self.fullscreen()
            self.show_all()
            
            # Create windows for additional monitors
            for i in range(1, n_monitors):
                print(f"Creating secondary window for monitor {i}")
                monitor = display.get_monitor(i)
                window = NotificationWindow(self.event_data, is_primary=False, primary_window=self)
                geometry = monitor.get_geometry()
                window.move(geometry.x, geometry.y)
                window.fullscreen()
                window.show_all()
                self.windows.append(window)
                window.connect("destroy", self.on_window_destroyed)
    
    def on_window_destroyed(self, window):
        """Handle window destruction."""
        if self.is_primary and window in self.windows:
            self.windows.remove(window)
            if len(self.windows) <= 1:  # Only primary window left
                self.destroy()
    
    def on_dismiss_clicked(self, button):
        """Handle dismiss button click."""
        print(f"Dismiss button clicked on {'primary' if self.is_primary else 'secondary'} window")
        self.was_dismissed = True
        
        if self.is_primary:
            # Primary window: close all windows
            print("Primary window closing all windows")
            windows_to_close = self.windows.copy()
            for window in windows_to_close:
                if window != self:
                    window.was_dismissed = True
                    window.destroy()
            self.destroy()
        else:
            # Secondary window: signal primary to handle dismiss
            print("Secondary window signaling primary")
            if self.primary_window:
                print("Found primary window, triggering dismiss")
                self.primary_window.on_dismiss_clicked(None)
            else:
                print("No primary window found, destroying self")
                self.destroy()
    
    def on_snooze_clicked(self, button):
        """Handle snooze button click."""
        if self.is_primary:
            # Primary window: close all and set snooze
            windows_to_close = self.windows.copy()
            for window in windows_to_close:
                if window != self:  # Don't destroy self yet
                    window.destroy()
            self.destroy()
            GLib.timeout_add_seconds(300, self.show_again)  # 5 minutes
        else:
            # Secondary window: signal primary to handle snooze
            primary_window = None
            for window in self.windows:
                if window.is_primary:
                    primary_window = window
                    break
                    
            if primary_window and not primary_window.was_dismissed:
                primary_window.on_snooze_clicked(None)  # Trigger snooze on primary
            else:
                self.destroy()  # Fallback if primary is gone
    
    def show_again(self):
        """Show the notification again after snooze."""
        new_notification = NotificationWindow(self.event_data, is_primary=True)
        new_notification.show_all()
        return False  # Don't repeat
    
    def on_join_clicked(self, button, url):
        """Handle join meeting button click."""
        Gtk.show_uri_on_window(None, url, Gdk.CURRENT_TIME)
        if self.is_primary:
            # Primary window: close all windows
            for window in self.windows:
                if window != self:  # Don't destroy self yet
                    window.destroy()
            self.destroy()
        else:
            # Secondary window: signal primary to handle join
            primary_window = self.windows[0]  # Primary window is always first
            if primary_window and not primary_window.was_dismissed:
                primary_window.on_join_clicked(None, url)  # Trigger join on primary
            else:
                self.destroy()  # Fallback if primary is gone
    
    def on_draw(self, widget, cr):
        """Handle window drawing for background image and color."""
        # Get window dimensions
        allocation = widget.get_allocation()
        width = allocation.width
        height = allocation.height

        # Draw background color
        bg_color = self.settings.get('background_color', 'rgba(0, 0, 0, 0.9)')
        rgba = Gdk.RGBA()
        rgba.parse(bg_color)
        cr.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
        cr.paint()

        # Draw background image if set
        bg_image = self.settings.get('background_image')
        if bg_image and os.path.exists(bg_image):
            try:
                # Load the image and scale it to fill the window while maintaining aspect ratio
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(bg_image)
                
                # Calculate scaling to cover the entire window
                scale_x = width / pixbuf.get_width()
                scale_y = height / pixbuf.get_height()
                scale = max(scale_x, scale_y)
                
                new_width = int(pixbuf.get_width() * scale)
                new_height = int(pixbuf.get_height() * scale)
                
                # Center the image
                x_offset = (width - new_width) // 2
                y_offset = (height - new_height) // 2
                
                # Scale the image
                scaled_pixbuf = pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
                
                # Draw the image
                Gdk.cairo_set_source_pixbuf(cr, scaled_pixbuf, x_offset, y_offset)
                cr.paint_with_alpha(0.7)  # Increased opacity for better visibility
                
            except Exception as e:
                print(f"Error loading background image: {e}")

        return False 