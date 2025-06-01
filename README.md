# ytmusic_wrapper

A Home Assistant custom component to control YouTube Music via the API of https://github.com/th-ch/youtube-music.
Requires a running instance of Youtube Music for initial setup.

# Installation

1. Enable the API Server in the YouTube Music app. Make sure to set the Authorization Strategy to No authorization.
2. Restart the YouTube Music app.
3. Install the custom component by adding this repository as custom repository in HACS.
4. Restart Home Assistant.
5. You can find the integration by searching for Youtube Music Wrapper in the integrations page.

# Features

Currently supports most features, including:
- Play/Pause
- Next/Previous track
- Volume control
- Seek
- Shuffle
- Clear queue