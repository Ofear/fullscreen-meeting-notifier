#!/usr/bin/env python3
"""Release helper script for Meeting Notifier."""
import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path

def update_version(version_file, new_version):
    """Update version numbers in version.py."""
    major, minor, patch = map(int, new_version.split('.'))
    content = []
    
    with open(version_file, 'r') as f:
        for line in f:
            if 'VERSION_MAJOR =' in line:
                line = f'VERSION_MAJOR = {major}  # For incompatible API changes\n'
            elif 'VERSION_MINOR =' in line:
                line = f'VERSION_MINOR = {minor}  # For backwards-compatible functionality\n'
            elif 'VERSION_PATCH =' in line:
                line = f'VERSION_PATCH = {patch}  # For backwards-compatible bug fixes\n'
            elif 'LAST_UPDATE =' in line:
                line = f'LAST_UPDATE = "{datetime.now().strftime("%Y-%m-%d")}"\n'
            content.append(line)
    
    with open(version_file, 'w') as f:
        f.writelines(content)

def update_debian_control(control_file, new_version):
    """Update version in debian/DEBIAN/control."""
    content = []
    with open(control_file, 'r') as f:
        for line in f:
            if line.startswith('Version:'):
                line = f'Version: {new_version}\n'
            content.append(line)
    
    with open(control_file, 'w') as f:
        f.writelines(content)

def update_appimage_builder(builder_file, new_version):
    """Update version in AppImageBuilder.yml."""
    content = []
    with open(builder_file, 'r') as f:
        for line in f:
            if 'version:' in line and not line.startswith('version:'):
                line = f'    version: {new_version}\n'
            content.append(line)
    
    with open(builder_file, 'w') as f:
        f.writelines(content)

def update_appstream_metadata(metadata_file, new_version):
    """Update version in AppStream metadata."""
    today = datetime.now().strftime("%Y-%m-%d")
    content = []
    with open(metadata_file, 'r') as f:
        for line in f:
            if '<release version=' in line:
                line = f'        <release version="{new_version}" date="{today}">\n'
            content.append(line)
    
    with open(metadata_file, 'w') as f:
        f.writelines(content)

def update_setup_py(setup_file, new_version):
    """Update version in setup.py."""
    content = []
    with open(setup_file, 'r') as f:
        for line in f:
            if 'version=' in line:
                line = f'    version="{new_version}",\n'
            content.append(line)
    
    with open(setup_file, 'w') as f:
        f.writelines(content)

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: release.py NEW_VERSION")
        print("Example: release.py 1.1.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("Error: Version must be in format X.Y.Z")
        sys.exit(1)
    
    # Get project root directory
    root_dir = Path(__file__).parent.parent
    
    # Update version in all necessary files
    files_to_update = {
        'src/version.py': update_version,
        'debian/DEBIAN/control': update_debian_control,
        'AppImageBuilder.yml': update_appimage_builder,
        'AppDir/usr/share/metainfo/fullscreen-meeting-notifier.appdata.xml': update_appstream_metadata,
        'setup.py': update_setup_py
    }
    
    for file_path, update_func in files_to_update.items():
        full_path = root_dir / file_path
        if full_path.exists():
            print(f"Updating {file_path}...")
            update_func(full_path, new_version)
        else:
            print(f"Warning: {file_path} not found")
    
    print("\nVersion updated successfully!")
    print("\nNext steps:")
    print("1. Review and update CHANGELOG.md")
    print("2. Commit changes:")
    print(f"   git commit -am 'Release version {new_version}'")
    print(f"3. Tag the release: git tag -a v{new_version} -m 'Version {new_version}'")
    print("4. Build packages:")
    print("   - AppImage: ./appimagetool AppDir FullScreenMeetingNotifier-x86_64.AppImage")
    print(f"   - Debian: dpkg-deb --build debian fullscreen-meeting-notifier_{new_version}_all.deb")
    print("5. Create GitHub release and upload packages")

if __name__ == '__main__':
    main() 