from setuptools import setup, find_packages

setup(
    name="fullscreen-meeting-notifier",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'PyGObject',
        'pytz'
    ],
    entry_points={
        'console_scripts': [
            'fullscreen-meeting-notifier=src.main:main',
        ],
    },
    data_files=[
        ('share/applications', ['fullscreen-meeting-notifier.desktop']),
        ('share/icons/hicolor/scalable/apps', ['icons/fullscreen-meeting-notifier.svg']),
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A full-screen meeting notifier that shows notifications across all monitors",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="meeting notification calendar google-calendar gtk",
    url="https://github.com/yourusername/fullscreen-meeting-notifier",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires='>=3.6',
) 