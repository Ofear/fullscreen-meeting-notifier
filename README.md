# FullScreen Meeting Notifier

A full-screen meeting notification application that displays upcoming Google Calendar meetings across all monitors. Perfect for ensuring you never miss a meeting, even when you're deeply focused on work.

## Features

- Full-screen notifications on all connected monitors
- Google Calendar integration
- Meeting join links detection (Zoom, etc.)
- Customizable appearance (background color, opacity, etc.)
- Sound notifications
- Snooze functionality
- System tray integration

## Requirements

- Python 3.6 or higher
- GTK 3.0
- FFmpeg (for sound notifications)
- Google account with Calendar access

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 ffmpeg

# Fedora
sudo dnf install python3-gobject gtk3 libappindicator-gtk3 ffmpeg

# Arch Linux
sudo pacman -S python-gobject gtk3 libappindicator-gtk3 ffmpeg
```

## Installation

### From PyPI (Recommended)

```bash
pip install fullscreen-meeting-notifier
```

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fullscreen-meeting-notifier.git
   cd fullscreen-meeting-notifier
   ```

2. Install the package:
   ```bash
   pip install .
   ```

## First Run Setup

1. Launch the application:
   ```bash
   fullscreen-meeting-notifier
   ```

2. On first run, you'll be prompted to authenticate with your Google account
3. Grant the necessary calendar permissions
4. The application will start running in your system tray

## Configuration

Settings can be configured through the application's settings window, accessible from the system tray icon.

You can customize:
- Background color and opacity
- Notification sound
- Text colors
- Background image

Settings are stored in `~/.config/meeting-notifier/settings.json`

## Usage

- The application runs in the system tray
- Click the tray icon to:
  - View today's meetings
  - Access settings
  - Check for meetings manually
  - Quit the application
- When a meeting is about to start:
  - Full-screen notifications appear on all monitors
  - A sound notification plays (if enabled)
  - You can:
    - Join the meeting (if a meeting link is detected)
    - Dismiss the notification
    - Snooze for 5 minutes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

