import os
import sys
import json
import random
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markup import escape

# Try to import TermImage, which may have different import paths
try:
    from term_image.image import TermImage
except ImportError:
    try:
        from term_image import TermImage
    except ImportError:
        TermImage = None

# --- Configuration and Utility Functions ---

def load_config():
    """Loads a configuration file, creating a default if none exists."""
    config_file = 'reaganplayer.json'
    default_config = {
        'music_folder': 'audio',
        'volume': 0.5,
        'shuffle_on': False,
        'page_size': 10,
        'current_page': 0
    }
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            # Ensure all keys are present
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]
    except (FileNotFoundError, json.JSONDecodeError):
        config = default_config
        save_config(config)
    return config

def save_config(config):
    """Saves the current configuration to a file."""
    config_file = 'reaganplayer.json'
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving configuration: {e}")

def get_music_info(file_path):
    """Extracts metadata (title, artist) from an audio file using mutagen."""
    try:
        from mutagen.easyid3 import EasyID3
        tags = EasyID3(file_path)
        title = tags.get('title', [os.path.basename(file_path)])[0]
        artist = tags.get('artist', ['Unknown Artist'])[0]
        return f"{title} - {artist}"
    except ImportError:
        return os.path.basename(file_path)
    except Exception:
        return os.path.basename(file_path)

def get_album_art_path(current_path):
    """Finds a common album art file in the current directory."""
    album_art_names = ('folder', 'cover', 'front')
    for filename in os.listdir(current_path):
        name, ext = os.path.splitext(filename.lower())
        if ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'):
            if any(art_name in name for art_name in album_art_names):
                return os.path.join(current_path, filename)
    return None

def display_image_in_terminal(console, image_path):
    """
    Displays an image in the terminal using the best available protocol.
    Added console as an argument for consistency.
    """
    if not os.path.exists(image_path) or not TermImage:
        return
    try:
        image = TermImage.from_file(image_path)
        image.draw()
        console.print("\n")
    except Exception as e:
        console.print(f"[bold red]Warning:[/bold red] Could not display album art. {e}")
        return

def play_song(pygame, console, song_path):
    """Loads and plays a song."""
    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        return True
    except pygame.error as e:
        console.print(f"[bold red]Error loading song:[/bold red] {os.path.basename(song_path)} - {e}")
        return False

# --- Multi-Column Printing Function ---

def print_in_columns(items, console, indent=0, pad=3):
    """
    Prints a list of strings in multiple columns to make better use of terminal space.
    The length of the string is calculated without rich formatting codes.
    """
    if not items:
        return

    # Get terminal width
    term_width = shutil.get_terminal_size().columns

    # Calculate column width based on the longest item's plain text length
    max_len = max(len(Text.from_markup(item).plain) for item in items)
    col_width = max_len + pad

    # Calculate number of columns
    n_cols = max(1, (term_width - indent) // col_width)

    # Calculate number of rows
    n_rows = (len(items) + n_cols - 1) // n_cols

    # Organize items into rows for printing
    for row in range(n_rows):
        line = Text()
        for col in range(n_cols):
            idx = col * n_rows + row
            if idx < len(items):
                item_text = Text.from_markup(items[idx])

                # Calculate padding needed for this specific item
                current_len = len(item_text.plain)
                padding_needed = max(0, col_width - current_len)

                # Append the item and the required padding as a single Text object
                line.append(item_text)
                line.append(" " * padding_needed)

        console.print(" " * indent, line)

# --- Main Player Functions ---
def draw_player_controls(pygame, console, config, now_playing_song, is_paused, queue):
    """Draws the dynamic player controls at the bottom of the screen."""
    if pygame.mixer.music.get_busy() or is_paused:
        if now_playing_song:
            song_info = get_music_info(now_playing_song)
            console.print(f"\n[bold green]Now Playing:[/bold green] {escape(song_info)} | [bold blue]Volume:[/bold blue] {int(config['volume'] * 100)}%")
        else:
            console.print("\n[dim]No song is currently playing.[/dim]")
    else:
        console.print("\n[dim]No song is currently playing.[/dim]")

    if queue:
        queue_list = "\n".join([f"  [dim]-[/dim] {escape(get_music_info(s))}" for s in queue])
        queue_panel = Panel(
            f"[bold cyan]Current Queue:[/bold cyan]\n{queue_list}",
            border_style="cyan"
        )
        console.print(queue_panel)

    # FIX: Corrected all Rich markup to ensure proper nesting and matching tags.
    console.print("\n[bold yellow]Queue Commands:[/bold yellow] [bold cyan]add[/bold cyan] (add to queue) | [bold cyan]clear[/bold cyan] (clear queue)")

    # FIX: Ensure all tags are correctly closed.
    console.print("[bold yellow]Playback Controls:[/bold yellow] [bold red]>[/bold red] (next) | [bold red]<[/bold red] (previous) | [bold red]+[/bold red] (vol up) | [bold red]-[/bold red] (vol down) | [bold red]t[/bold red] (toggle shuffle) | [bold red]s[/bold red] (shuffle & play) | [bold red]pause[/bold red] (pause/unpause) | [bold red]q[/bold red] (quit)")

def reaganPLAYER():
    """A terminal-based music player with folder navigation and continuous playback."""
    console = Console()
    sys.stdout.write("\x1b]2;reaganPLAYER\x07")

    try:
        import pygame
    except ImportError:
        console.print("[bold red]Error:[/bold red] The 'pygame' library is not installed. Please install it with 'pip install pygame'.")
        return

    try:
        pygame.mixer.init()
        pygame.display.init()
    except pygame.error as e:
        console.print(f"[bold red]Error:[/bold red] Could not initialize mixer. Please check your audio drivers. {e}")
        return

    config = load_config()
    pygame.mixer.music.set_volume(config['volume'])
    pygame.mixer.music.set_endevent(pygame.USEREVENT)

    last_used_path = config['music_folder']
    now_playing_song = None
    is_paused = False
    queue = []

    # FIX: Corrected Rich markup to match opening and closing tags.
    welcome_panel_text = Text()
    welcome_panel_text.append("reaganPLAYER\n\n")
    welcome_panel_text.append("Press Enter to use the last path: ")
    welcome_panel_text.append(f"{last_used_path}\n")
    welcome_panel_text.append("or type a new path and press Enter.")

    console.print(Panel(
        welcome_panel_text,
        title="Welcome!",
        border_style="bold blue"
    ))

    music_folder_input = input("Music folder path: ").strip()
    music_folder = music_folder_input or last_used_path

    config['music_folder'] = music_folder
    save_config(config)

    if not os.path.isdir(music_folder):
        console.print(f"[bold red]Error:[/bold red] The directory '{music_folder}' does not exist or is not a directory.")
        return

    current_path = os.path.abspath(music_folder)
    current_playlist = []
    current_song_index = -1

    audio_extensions = (
        '.mp3', '.wav', '.ogg', '.flac', '.aiff', '.aif', '.m4a', '.aac'
    )

    while True:
        # We need to process events to keep the audio playing and responding
        # to the end-of-track event.
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                if queue:
                    next_song = queue.pop(0)
                    play_song(pygame, console, next_song)
                    now_playing_song = next_song
                    current_song_index = -1
                elif current_playlist:
                    current_song_index = (current_song_index + 1) % len(current_playlist)
                    play_song(pygame, console, current_playlist[current_song_index])
                    now_playing_song = current_playlist[current_song_index]

        console.clear()

        try:
            all_contents = sorted(os.listdir(current_path))
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/bold red] Directory '{current_path}' not found. Returning to the main prompt.")
            return

        folders = [d for d in all_contents if os.path.isdir(os.path.join(current_path, d))]
        audio_files = [f for f in all_contents if f.endswith(audio_extensions)]

        start_index = config['current_page'] * config['page_size']
        end_index = start_index + config['page_size']

        view_playlist = [os.path.join(current_path, f) for f in audio_files]
        paginated_audio_files = audio_files[start_index:end_index]


        console.print(f"\n[red]reagan[/red][bold white]PLAYER[/bold white]")
        console.print(f"\n[bold green]Current Directory:[/bold green] {current_path}")
        console.print(f"[bold magenta]Shuffle Mode:[/bold magenta] {'On' if config['shuffle_on'] else 'Off'}")
        console.print("--------------------------------------------------")

        item_map = {}
        items_to_print = []
        item_counter = 1

        if current_path != os.path.abspath(music_folder):
            items_to_print.append(f"[bold yellow]{item_counter}.[/bold yellow] [blue]DIR[/blue] ..")
            item_map[item_counter] = ".."
            item_counter += 1

        for folder in folders:
            items_to_print.append(f"[bold yellow]{item_counter}.[/bold yellow] [blue]DIR[/blue] {folder}")
            item_map[item_counter] = os.path.join(current_path, folder)
            item_counter += 1

        for audio in paginated_audio_files:
            info = get_music_info(os.path.join(current_path, audio))
            items_to_print.append(f"[bold yellow]{item_counter}.[/bold yellow] [green]SONG[/green] {escape(info)}")
            item_map[item_counter] = os.path.join(current_path, audio)
            item_counter += 1

        print_in_columns(items_to_print, console, indent=2)

        if len(audio_files) > config['page_size']:
            console.print("\n[bold]Pagination:[/bold] [bold blue]n[/bold blue] (next page) | [bold blue]p[/bold blue] (previous page)")

        console.print("\n")

        draw_player_controls(pygame, console, config, now_playing_song, is_paused, queue)

        choice = input("Enter a number to select, or a command: ").strip().lower()

        if choice == 'add':
            try:
                add_choice = int(input("Enter number of song to add to queue: ").strip())
                if add_choice in item_map and os.path.isfile(item_map[add_choice]):
                    queue.append(item_map[add_choice])
                    console.print(f"[bold green]Added to queue:[/bold green] {escape(get_music_info(item_map[add_choice]))}")
                else:
                    console.print("[bold red]Invalid selection. Please enter the number of a song to add.[/bold red]")
                input("Press Enter to continue...")
            except (ValueError, IndexError):
                console.print("[bold red]Invalid input. Please enter a valid number.[/bold red]")
            continue
        elif choice == 'clear':
            queue.clear()
            console.print("[bold green]Queue cleared.[/bold green]")
            input("Press Enter to continue...")
            continue

        elif choice == '+':
            config['volume'] = min(1.0, config['volume'] + 0.1)
            pygame.mixer.music.set_volume(config['volume'])
            save_config(config)
            continue
        elif choice == '-':
            config['volume'] = max(0.0, config['volume'] - 0.1)
            pygame.mixer.music.set_volume(config['volume'])
            save_config(config)
            continue
        elif choice in ('pause', ' '):
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                is_paused = True
            elif is_paused:
                pygame.mixer.music.unpause()
                is_paused = False
            continue
        elif choice == '>':
            if queue:
                next_song = queue.pop(0)
                play_song(pygame, console, next_song)
                now_playing_song = next_song
                current_song_index = -1
            elif current_playlist and current_song_index != -1:
                current_song_index = (current_song_index + 1) % len(current_playlist)
                play_song(pygame, console, current_playlist[current_song_index])
                now_playing_song = current_playlist[current_song_index]
            continue
        elif choice == '<':
            if current_playlist and current_song_index != -1:
                current_song_index = (current_song_index - 1 + len(current_playlist)) % len(current_playlist)
                play_song(pygame, console, current_playlist[current_song_index])
                now_playing_song = current_playlist[current_song_index]
            continue
        elif choice == 's':
            if view_playlist:
                config['shuffle_on'] = True
                save_config(config)
                current_playlist = view_playlist.copy()
                random.shuffle(current_playlist)
                current_song_index = 0
                play_song(pygame, console, current_playlist[current_song_index])
                now_playing_song = current_playlist[current_song_index]
            continue
        elif choice == 't':
            config['shuffle_on'] = not config['shuffle_on']
            save_config(config)
            if config['shuffle_on']:
                current_playlist = view_playlist.copy()
                random.shuffle(current_playlist)
            else:
                current_playlist = sorted(view_playlist)
            if now_playing_song and pygame.mixer.music.get_busy() and current_song_index != -1:
                try:
                    current_song_index = current_playlist.index(now_playing_song)
                except ValueError:
                    current_song_index = -1
            continue
        elif choice == 'q':
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.quit()
            console.print("[bold red]Exiting reaganPLAYER. Come back soon![/bold red]")
            break
        elif choice == 'n':
            if start_index + config['page_size'] < len(audio_files):
                config['current_page'] += 1
            else:
                config['current_page'] = 0
            save_config(config)
            continue
        elif choice == 'p':
            config['current_page'] = max(0, config['current_page'] - 1)
            save_config(config)
            continue

        try:
            choice_num = int(choice)
            if choice_num in item_map:
                selected_item_path = item_map[choice_num]
                if selected_item_path == "..":
                    current_path = os.path.dirname(current_path)
                    config['current_page'] = 0
                    save_config(config)
                elif os.path.isdir(selected_item_path):
                    current_path = selected_item_path
                    config['current_page'] = 0
                    save_config(config)
                elif os.path.isfile(selected_item_path):
                    if config['shuffle_on']:
                        current_playlist = view_playlist.copy()
                        random.shuffle(current_playlist)
                    else:
                        current_playlist = sorted(view_playlist)
                    try:
                        current_song_index = current_playlist.index(selected_item_path)
                    except ValueError:
                        current_song_index = 0
                    play_song(pygame, console, current_playlist[current_song_index])
                    now_playing_song = current_playlist[current_song_index]
            else:
                console.print("[bold red]Invalid number. Please try again.[/bold red]")
        except (ValueError, IndexError):
            console.print("[bold red]Invalid input. Please enter a number or a valid command.[/bold red]")

if __name__ == "__main__":
    reaganPLAYER()
