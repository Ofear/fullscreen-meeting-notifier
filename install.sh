#!/bin/bash

# Exit on error
set -e

# Get the script's directory
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
APP_NAME="FullScreenMeetingNotifier"
APPIMAGE_NAME="${APP_NAME}-x86_64.AppImage"

# Check if AppImage exists
if [ ! -f "${SCRIPT_DIR}/${APPIMAGE_NAME}" ]; then
    echo "Error: ${APPIMAGE_NAME} not found in the current directory"
    exit 1
fi

# Make AppImage executable
chmod +x "${SCRIPT_DIR}/${APPIMAGE_NAME}"

# Create applications directory if it doesn't exist
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons/hicolor/scalable/apps

# Copy AppImage to bin directory
cp "${SCRIPT_DIR}/${APPIMAGE_NAME}" ~/.local/bin/

# Extract icon from AppImage
cd ~/.local/share/icons/hicolor/scalable/apps/
"${SCRIPT_DIR}/${APPIMAGE_NAME}" --appimage-extract fullscreen-meeting-notifier.svg > /dev/null 2>&1
mv squashfs-root/fullscreen-meeting-notifier.svg .
rm -rf squashfs-root
cd "${SCRIPT_DIR}"

# Create desktop entry
cat > ~/.local/share/applications/fullscreen-meeting-notifier.desktop << EOF
[Desktop Entry]
Type=Application
Name=FullScreen Meeting Notifier
Comment=Full-screen meeting notifications across all monitors
Exec=${HOME}/.local/bin/${APPIMAGE_NAME}
Icon=fullscreen-meeting-notifier
Terminal=false
Categories=Office;Calendar;
Keywords=meeting;notification;calendar;google;
StartupNotify=true
EOF

# Update desktop database
update-desktop-database ~/.local/share/applications || true

echo "Installation complete!"
echo "You can now:"
echo "1. Run the application from your applications menu"
echo "2. Run it from the terminal with: ${APPIMAGE_NAME}"
echo "3. Double-click ${HOME}/.local/bin/${APPIMAGE_NAME}"

# Ask if user wants to run the application now
read -p "Would you like to run the application now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    "${HOME}/.local/bin/${APPIMAGE_NAME}" &
fi 