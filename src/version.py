"""Version information for the application."""

# Follow Semantic Versioning (https://semver.org/)
VERSION_MAJOR = 1  # For incompatible API changes
VERSION_MINOR = 0  # For backwards-compatible functionality
VERSION_PATCH = 0  # For backwards-compatible bug fixes
VERSION_SUFFIX = ''  # For pre-release versions like 'alpha', 'beta', 'rc1'

# Construct version string
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}{VERSION_SUFFIX}"

# Update date in ISO format
LAST_UPDATE = "2024-04-07"

def get_version():
    """Return the current version string."""
    return VERSION

def get_version_tuple():
    """Return version as a tuple (major, minor, patch)."""
    return (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

def get_update_date():
    """Return the last update date."""
    return LAST_UPDATE 