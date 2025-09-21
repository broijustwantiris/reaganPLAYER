<img width="1920" height="1080" alt="2025-09-20-215109_hyprshot" src="https://github.com/user-attachments/assets/2ebb34e5-53ed-4e0c-9266-145f24a31939" />


# ReaganPLAYER

ReaganPLAYER is a lightweight, terminal-based music player designed for simplicity and efficiency. Built with Python, it provides a text-based interface for navigating your music library, playing audio files, and managing playback, all without leaving your command line.

## Features

  - **Intuitive Navigation**: Easily browse your music folders directly from the terminal.
  - **Audio Playback**: Supports a wide range of audio formats including `.mp3`, `.wav`, and `.flac`.
  - **Playback Controls**: Control your music with simple commands for play, pause, next track, and previous track.
  - **Volume Control**: Adjust the volume up or down directly from the command line.
  - **Shuffle Mode**: Toggle shuffle on or off for random playback of your music library.
  - **Queue Management**: Add specific songs to a queue to listen to them in a custom order.
  - **Terminal Album Art**: Displays album art in the terminal using `term_image` if available.
  - **User-friendly Interface**: A clean, colorful interface built with the `rich` library for an enhanced user experience.

## Installation

### Prerequisites

  - Python 3.6 or higher
  - `pip` (Python package installer)

### Step-by-Step Installation

1.  **Clone the Repository (if applicable) or Download the Script**:

    ```bash
    git clone https://github.com/broijustwantiris/reaganplayer.git
    cd reaganplayer
    ```

2.  **Install the Required Libraries**:
    ReaganPLAYER relies on a few key libraries that can be installed using `pip`.

    ```bash
    pip install pygame rich mutagen term-image
    ```

      - `pygame`: Handles audio playback.
      - `rich`: Provides the colorful and formatted terminal interface.
      - `mutagen`: Used to read metadata (like title and artist) from audio files.
      - `term-image`: An optional library for displaying images in the terminal.

## Usage

1.  **Run the Player**:
    Navigate to the directory where you saved `reaganplayer.py` and run the script from your terminal.

    ```bash
    python3 reaganplayer.py
    ```

2.  **Select Your Music Folder**:
    Upon launching, the player will prompt you for the path to your music folder. You can enter a path or press `Enter` to use the default (`audio/` within the script's directory).

3.  **Basic Commands**:

      - **Numbers (`1`, `2`, `3`, etc.)**: Select a folder to navigate or a song to play.
      - **`+`**: Increase volume.
      - **`-`**: Decrease volume.
      - **`>`**: Play the next song in the queue or playlist.
      - **`<`**: Play the previous song.
      - **`t`**: Toggle shuffle mode on/off.
      - **`s`**: Shuffle the playlist and start playing from the first shuffled track.
      - **`add`**: Add a song to the playback queue.
      - **`clear`**: Clear the current playback queue.
      - **`pause` or `spacebar`**: Pause or unpause the current song.
      - **`q`**: Quit the player.

## Configuration

ReaganPLAYER creates a configuration file named `reaganplayer.json` in the same directory as the script. You can edit this file to change settings like the default music folder, initial volume, and page size.

## Troubleshooting

  - **Colors not showing?**
    Ensure your terminal supports 256-color or true-color output. The `rich` library automatically detects terminal capabilities.
  - **`ImportError: No module named 'pygame'`**
    You need to install the required libraries. Run the command: `pip install pygame rich mutagen term-image`.
  - **Player crashes on startup?**
    This may be due to a `pygame` audio driver issue. Ensure your system's audio drivers are up to date and compatible with `pygame`.
  - **Music metadata not showing?**
    Check that your music files have proper ID3 tags. The `mutagen` library reads this information. If tags are missing, the filename will be used as a fallback.
