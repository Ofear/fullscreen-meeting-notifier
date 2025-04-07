"""Settings window for Meeting Notifier."""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import json
import os
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SettingsWindow(Gtk.Window):
    """Settings window for customizing notifications."""
    
    def __init__(self, parent_settings=None):
        logger.debug("Initializing Settings Window")
        super().__init__(title="Meeting Notifier Settings")
        
        # Initialize settings with defaults
        self.settings = {
            'background_color': 'rgba(0, 0, 0, 0.9)',
            'background_image': '',
            'notification_sound': '',  # Will be set after checking available sounds
            'sound_enabled': True,
            'text_color': '#ffffff',
            'button_color': '#4a4a4a',
            'button_text_color': '#ffffff',
            'opacity': 0.85
        }
        
        # Load existing settings if available
        self.settings_file = os.path.expanduser('~/.config/meeting-notifier/settings.json')
        
        # If parent settings are provided, use them instead of loading from file
        if parent_settings:
            logger.debug(f"Using parent settings: {parent_settings}")
            self.settings.update(parent_settings)
        else:
            logger.debug("Loading settings from file")
            self.load_settings()
        
        # Set default sound if none is set
        if not self.settings['notification_sound']:
            logger.debug("No notification sound set, setting default")
            self.set_default_sound()
            
        logger.debug(f"Current settings after initialization: {self.settings}")
        
        # Set up window properties
        self.set_default_size(600, 500)
        self.set_border_width(0)  # Remove border for modern look
        
        # Create header bar with modern styling
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title("Settings")
        header_bar.set_decoration_layout("menu:minimize,maximize,close")
        self.set_titlebar(header_bar)
        self.set_decorated(True)  # Enable window decorations

        # Add CSS styling
        style_provider = Gtk.CssProvider()
        css = """
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
            }
            headerbar button.titlebutton.close {
                background-color: transparent;
                color: white;
                opacity: 0.8;
            }
            headerbar button.titlebutton.close:hover {
                background-color: #e74c3c;
                opacity: 1;
            }
            headerbar button.titlebutton.maximize {
                background-color: transparent;
                color: white;
                opacity: 0.8;
            }
            headerbar button.titlebutton.minimize {
                background-color: transparent;
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
            .settings-frame {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px;
                margin: 10px;
                background-color: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .settings-frame > label {
                margin: 5px;
                color: #2c3e50;
                font-weight: bold;
            }
            .settings-label {
                color: #2c3e50;
                margin: 5px 10px;
            }
            button {
                background: linear-gradient(to bottom, #3498db, #2980b9);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            }
            button:hover {
                background: linear-gradient(to bottom, #3cb0fd, #3498db);
            }
            .save-button {
                background: linear-gradient(to bottom, #27ae60, #2ecc71);
                font-weight: bold;
                padding: 10px 20px;
                margin: 15px;
            }
            .save-button:hover {
                background: linear-gradient(to bottom, #2ecc71, #27ae60);
            }
            .notebook {
                border: none;
            }
            .notebook tab {
                padding: 8px 15px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                color: #495057;
            }
            .notebook tab:checked {
                background-color: white;
                border-bottom: none;
                color: #2c3e50;
            }
            scale {
                margin: 10px;
            }
            scale trough {
                background-color: #e9ecef;
                border-radius: 10px;
                min-height: 6px;
            }
            scale highlight {
                background-color: #3498db;
                border-radius: 10px;
            }
            scale slider {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 50%;
                min-width: 18px;
                min-height: 18px;
            }
        """
        style_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Main container with padding
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.set_margin_top(15)
        main_box.set_margin_bottom(15)
        main_box.set_margin_start(15)
        main_box.set_margin_end(15)
        self.add(main_box)
        
        # Create notebook for tabs
        notebook = Gtk.Notebook()
        notebook.get_style_context().add_class('notebook')
        main_box.pack_start(notebook, True, True, 0)
        
        # Appearance tab
        appearance_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        appearance_box.set_margin_top(15)
        appearance_box.set_margin_bottom(15)
        appearance_box.set_margin_start(15)
        appearance_box.set_margin_end(15)
        
        # Background settings
        background_frame = Gtk.Frame(label="Background")
        background_frame.get_style_context().add_class('settings-frame')
        background_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        background_box.set_margin_top(10)
        background_box.set_margin_bottom(10)
        background_box.set_margin_start(10)
        background_box.set_margin_end(10)
        
        # Background color
        color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        color_label = Gtk.Label(label="Background Color:")
        color_label.get_style_context().add_class('settings-label')
        self.color_button = Gtk.ColorButton()
        self.color_button.set_use_alpha(True)
        # Set current color
        rgba = Gdk.RGBA()
        rgba.parse(self.settings['background_color'])
        self.color_button.set_rgba(rgba)
        self.color_button.connect("color-set", self.on_color_selected)
        color_box.pack_start(color_label, False, False, 0)
        color_box.pack_start(self.color_button, False, False, 0)
        background_box.pack_start(color_box, False, False, 0)
        
        # Background image
        image_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        image_label = Gtk.Label(label="Background Image:")
        image_label.get_style_context().add_class('settings-label')
        self.image_chooser = Gtk.FileChooserButton(title="Select Background Image")
        self.image_chooser.set_filter(self.create_image_filter())
        if self.settings['background_image']:
            self.image_chooser.set_filename(self.settings['background_image'])
        self.image_chooser.connect("file-set", self.on_image_selected)
        image_box.pack_start(image_label, False, False, 0)
        image_box.pack_start(self.image_chooser, True, True, 0)
        background_box.pack_start(image_box, False, False, 0)
        
        # Opacity
        opacity_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        opacity_label = Gtk.Label(label="Opacity:")
        opacity_label.get_style_context().add_class('settings-label')
        self.opacity_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 0.05)
        self.opacity_scale.set_value(self.settings['opacity'])
        self.opacity_scale.connect("value-changed", self.on_opacity_changed)
        opacity_box.pack_start(opacity_label, False, False, 0)
        opacity_box.pack_start(self.opacity_scale, True, True, 0)
        background_box.pack_start(opacity_box, False, False, 0)
        
        background_frame.add(background_box)
        appearance_box.pack_start(background_frame, False, False, 0)
        
        # Text settings
        text_frame = Gtk.Frame(label="Text")
        text_frame.get_style_context().add_class('settings-frame')
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        text_box.set_margin_top(10)
        text_box.set_margin_bottom(10)
        text_box.set_margin_start(10)
        text_box.set_margin_end(10)
        
        # Text color
        text_color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        text_color_label = Gtk.Label(label="Text Color:")
        text_color_label.get_style_context().add_class('settings-label')
        self.text_color_button = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(self.settings['text_color'])
        self.text_color_button.set_rgba(rgba)
        self.text_color_button.connect("color-set", self.on_text_color_selected)
        text_color_box.pack_start(text_color_label, False, False, 0)
        text_color_box.pack_start(self.text_color_button, False, False, 0)
        text_box.pack_start(text_color_box, False, False, 0)
        
        text_frame.add(text_box)
        appearance_box.pack_start(text_frame, False, False, 0)
        
        # Button settings
        button_frame = Gtk.Frame(label="Buttons")
        button_frame.get_style_context().add_class('settings-frame')
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        button_box.set_margin_top(10)
        button_box.set_margin_bottom(10)
        button_box.set_margin_start(10)
        button_box.set_margin_end(10)
        
        # Button color
        button_color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_color_label = Gtk.Label(label="Button Color:")
        button_color_label.get_style_context().add_class('settings-label')
        self.button_color_button = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(self.settings['button_color'])
        self.button_color_button.set_rgba(rgba)
        self.button_color_button.connect("color-set", self.on_button_color_selected)
        button_color_box.pack_start(button_color_label, False, False, 0)
        button_color_box.pack_start(self.button_color_button, False, False, 0)
        button_box.pack_start(button_color_box, False, False, 0)
        
        # Button text color
        button_text_color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_text_color_label = Gtk.Label(label="Button Text Color:")
        button_text_color_label.get_style_context().add_class('settings-label')
        self.button_text_color_button = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(self.settings['button_text_color'])
        self.button_text_color_button.set_rgba(rgba)
        self.button_text_color_button.connect("color-set", self.on_button_text_color_selected)
        button_text_color_box.pack_start(button_text_color_label, False, False, 0)
        button_text_color_box.pack_start(self.button_text_color_button, False, False, 0)
        button_box.pack_start(button_text_color_box, False, False, 0)
        
        button_frame.add(button_box)
        appearance_box.pack_start(button_frame, False, False, 0)
        
        notebook.append_page(appearance_box, Gtk.Label(label="Appearance"))
        
        # Sound tab
        sound_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        sound_box.set_margin_top(15)
        sound_box.set_margin_bottom(15)
        sound_box.set_margin_start(15)
        sound_box.set_margin_end(15)
        
        # Sound settings frame
        sound_frame = Gtk.Frame(label="Sound Settings")
        sound_frame.get_style_context().add_class('settings-frame')
        sound_settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        sound_settings_box.set_margin_top(10)
        sound_settings_box.set_margin_bottom(10)
        sound_settings_box.set_margin_start(10)
        sound_settings_box.set_margin_end(10)
        
        # Sound enable/disable switch
        sound_enable_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        sound_enable_label = Gtk.Label(label="Enable Sound:")
        sound_enable_label.get_style_context().add_class('settings-label')
        self.sound_switch = Gtk.Switch()
        self.sound_switch.set_active(self.settings.get('sound_enabled', True))
        self.sound_switch.connect("notify::active", self.on_sound_enabled_changed)
        sound_enable_box.pack_start(sound_enable_label, False, False, 0)
        sound_enable_box.pack_start(self.sound_switch, False, False, 0)
        sound_settings_box.pack_start(sound_enable_box, False, False, 0)
        
        # Add sound file chooser
        sound_settings_box.pack_start(self.create_sound_chooser(), False, False, 0)
        
        sound_frame.add(sound_settings_box)
        sound_box.pack_start(sound_frame, False, False, 0)
        
        notebook.append_page(sound_box, Gtk.Label(label="Sound"))
        
        # Save button
        save_button = Gtk.Button(label="Save Changes")
        save_button.get_style_context().add_class('save-button')
        save_button.connect("clicked", self.on_save_clicked)
        save_button.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(save_button, False, False, 0)
        
        self.show_all()
    
    def create_image_filter(self):
        """Create a file filter for image files."""
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image files")
        filter_images.add_mime_type("image/jpeg")
        filter_images.add_mime_type("image/png")
        return filter_images
    
    def create_sound_filter(self):
        """Create a file filter for sound files."""
        sound_filter = Gtk.FileFilter()
        sound_filter.set_name("Sound files")
        sound_filter.add_mime_type("audio/x-vorbis+ogg")
        sound_filter.add_mime_type("audio/ogg")
        sound_filter.add_mime_type("audio/mpeg")
        sound_filter.add_mime_type("audio/x-wav")
        sound_filter.add_pattern("*.ogg")
        sound_filter.add_pattern("*.oga")
        sound_filter.add_pattern("*.mp3")
        sound_filter.add_pattern("*.wav")
        return sound_filter
    
    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings.update(json.load(f))
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # Update settings before saving
            self.settings.update({
                'background_color': self.color_button.get_rgba().to_string(),
                'text_color': self.text_color_button.get_rgba().to_string(),
                'button_color': self.button_color_button.get_rgba().to_string(),
                'button_text_color': self.button_text_color_button.get_rgba().to_string(),
                'opacity': self.opacity_scale.get_value(),
                'sound_enabled': self.sound_switch.get_active(),
                'notification_sound': self.settings['notification_sound']  # Preserve the sound file path
            })
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
            # Add error dialog to show the error to the user
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error Saving Settings"
            )
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
    
    def on_color_selected(self, button):
        """Handle background color selection."""
        color = button.get_rgba()
        self.settings['background_color'] = color.to_string()
    
    def on_image_selected(self, button):
        """Handle background image selection."""
        filename = button.get_filename()
        if filename:
            # Copy the image to the config directory
            config_dir = os.path.dirname(self.settings_file)
            images_dir = os.path.join(config_dir, 'images')
            os.makedirs(images_dir, exist_ok=True)
            
            new_path = os.path.join(images_dir, os.path.basename(filename))
            shutil.copy2(filename, new_path)
            self.settings['background_image'] = new_path
    
    def on_opacity_changed(self, scale):
        """Handle opacity change."""
        self.settings['opacity'] = scale.get_value()
    
    def on_text_color_selected(self, button):
        """Handle text color selection."""
        color = button.get_rgba()
        self.settings['text_color'] = color.to_string()
    
    def on_button_color_selected(self, button):
        """Handle button color selection."""
        color = button.get_rgba()
        self.settings['button_color'] = color.to_string()
    
    def on_button_text_color_selected(self, button):
        """Handle button text color selection."""
        color = button.get_rgba()
        self.settings['button_text_color'] = color.to_string()
    
    def on_sound_selected(self, button):
        """Handle sound file selection."""
        filename = button.get_filename()
        if filename:
            # Copy the sound file to the config directory
            config_dir = os.path.dirname(self.settings_file)
            sounds_dir = os.path.join(config_dir, 'sounds')
            os.makedirs(sounds_dir, exist_ok=True)
            
            new_path = os.path.join(sounds_dir, os.path.basename(filename))
            shutil.copy2(filename, new_path)
            self.settings['notification_sound'] = new_path
    
    def play_sound(self, sound_file):
        """Play a sound file using available sound players."""
        if not sound_file or not os.path.exists(sound_file):
            logger.error(f"Sound file not found: {sound_file}")
            return False

        # List of possible sound players and their commands with high quality settings
        players = [
            ('ffplay', f'ffplay -nodisp -autoexit -loglevel quiet -af "volume=0.75" "{sound_file}"'),
            ('play', f'play -q "{sound_file}" vol 0.75'),  # from sox package
            ('aplay', f'aplay -q "{sound_file}"'),
            ('paplay', f'paplay --volume=32000 "{sound_file}"'),
        ]

        for player, command in players:
            # Check if the player is installed
            if os.system(f'which {player} >/dev/null 2>&1') == 0:
                try:
                    result = os.system(command)
                    if result == 0:
                        return True
                except Exception as e:
                    logger.error(f"Error playing sound with {player}: {e}")
                    continue

        # If we get here, no player worked
        logger.error("No available sound player found. Please install pulseaudio-utils, alsa-utils, sox, or ffmpeg")
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Sound Player Not Found"
        )
        dialog.format_secondary_text(
            "Please install one of the following packages to enable sound:\n"
            "- ffmpeg (recommended)\n"
            "- pulseaudio-utils\n"
            "- alsa-utils\n"
            "- sox"
        )
        dialog.run()
        dialog.destroy()
        return False

    def on_test_sound(self, button):
        """Play the selected notification sound."""
        if self.settings['notification_sound'] and os.path.exists(self.settings['notification_sound']):
            self.play_sound(self.settings['notification_sound'])
    
    def on_sound_enabled_changed(self, switch, gparam):
        """Handle sound enable/disable switch changes."""
        self.settings['sound_enabled'] = switch.get_active()
    
    def on_save_clicked(self, button):
        """Save settings and close window."""
        self.save_settings()
        self.destroy()
    
    def set_default_sound(self):
        """Set the default notification sound by checking common system sound locations."""
        possible_sounds = [
            # High quality notification sounds
            '/usr/share/sounds/freedesktop/stereo/message-new-instant.oga',
            '/usr/share/sounds/ubuntu/stereo/message-new-instant.ogg',
            '/usr/share/sounds/gnome/default/alerts/glass.ogg',
            '/usr/share/sounds/purple/receive.wav',
            # Fallback to other sounds if high quality ones aren't available
            '/usr/share/sounds/freedesktop/stereo/message.oga',
            '/usr/share/sounds/ubuntu/stereo/message.ogg',
            '/usr/share/sounds/gnome/default/alerts/drip.ogg'
        ]
        
        # First check for bundled sound
        bundled_sound = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'resources', 'sounds', 'notification.ogg')
        if os.path.exists(bundled_sound):
            self.settings['notification_sound'] = bundled_sound
            return
        
        # Then check system sounds
        for sound_path in possible_sounds:
            if os.path.exists(sound_path):
                self.settings['notification_sound'] = sound_path
                return
        
        # If no sounds found, create a config directory and copy a default sound
        try:
            config_dir = os.path.dirname(self.settings_file)
            sounds_dir = os.path.join(config_dir, 'sounds')
            os.makedirs(sounds_dir, exist_ok=True)
            
            # Copy the first available system sound to our config directory
            for sound_path in possible_sounds:
                if os.path.exists(sound_path):
                    dest_path = os.path.join(sounds_dir, 'notification.ogg')
                    shutil.copy2(sound_path, dest_path)
                    self.settings['notification_sound'] = dest_path
                    return
        except Exception as e:
            logger.error(f"Error setting up default sound: {e}")

    def create_sound_chooser(self):
        """Create and configure the sound file chooser button."""
        sound_file_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        sound_label = Gtk.Label(label="Notification Sound:")
        sound_label.get_style_context().add_class('settings-label')
        
        # Create file chooser button
        self.sound_chooser = Gtk.FileChooserButton(title="Select Notification Sound")
        self.sound_chooser.set_filter(self.create_sound_filter())
        
        # Set the current sound file if it exists
        if self.settings['notification_sound'] and os.path.exists(self.settings['notification_sound']):
            self.sound_chooser.set_filename(self.settings['notification_sound'])
        
        self.sound_chooser.connect("file-set", self.on_sound_selected)
        
        # Test sound button
        test_sound_button = Gtk.Button.new_with_label("Test Sound")
        test_sound_button.connect("clicked", self.on_test_sound)
        
        sound_file_box.pack_start(sound_label, False, False, 0)
        sound_file_box.pack_start(self.sound_chooser, True, True, 0)
        sound_file_box.pack_start(test_sound_button, False, False, 0)
        
        return sound_file_box 