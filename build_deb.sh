#!/bin/bash

# Exit on error
set -e

# Clean up any previous builds
rm -rf debian/usr/lib/python3/dist-packages/fullscreen_meeting_notifier/*
rm -rf debian/usr/share/applications/*
rm -rf debian/usr/share/icons/hicolor/scalable/apps/*

# Copy Python package
cp -r src/* debian/usr/lib/python3/dist-packages/fullscreen_meeting_notifier/

# Copy desktop file and icon
cp fullscreen-meeting-notifier.desktop debian/usr/share/applications/
cp icons/fullscreen-meeting-notifier.svg debian/usr/share/icons/hicolor/scalable/apps/

# Create executable script
mkdir -p debian/usr/bin
cat > debian/usr/bin/fullscreen-meeting-notifier << 'EOF'
#!/usr/bin/python3
import sys
sys.path.append('/usr/lib/python3/dist-packages')
from fullscreen_meeting_notifier.main import main
if __name__ == "__main__":
    main()
EOF

# Make executable
chmod 755 debian/usr/bin/fullscreen-meeting-notifier

# Set permissions
find debian -type d -exec chmod 755 {} \;
find debian -type f -exec chmod 644 {} \;
chmod 755 debian/DEBIAN/postinst
chmod 755 debian/usr/bin/fullscreen-meeting-notifier

# Build the package
dpkg-deb --build debian fullscreen-meeting-notifier_1.0.0_all.deb

echo "Package built: fullscreen-meeting-notifier_1.0.0_all.deb" 