import os
import sys
import time
from typing import List, Optional
from yt_dlp import YoutubeDL
from tqdm import tqdm
import re
 
# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def clean_ansi(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
 
def erase_previous_line() -> None:
    """Moves the cursor up one line and clears it."""
    sys.stdout.write("\033[1A\033[K")
    sys.stdout.flush()
 
def print_space() -> None:
    """Adds a blank line for visual breathing room."""
    print("")
 
def clear_screen() -> None:
    """Clears terminal based on OS."""
    os.system('cls' if os.name == 'nt' else 'clear')
def request_loop(text: str, option: list[str]) -> str:
    """
    Ask the user for some detail and repeats the request due to wrong input.
 
    Args:
 
        text(str): This is the input text the system will ask the user.
 
        option(list[str]): Contains the options the system must pick from
                           Remember the cases must be lower
 
    Return:
        str: The correct answer that the system needs.
    """
 
    print(f"\n{text}\n\nThese are the options you have:\n\n[ {' '.join(option)} ]\n")
    val = input("Choice: ").lower()
 
    while True:
 
        if val in option:
 
            return val  # Breaks this function and give the correct answer
 
        else:
            # Clears the past 8 lines above (AI by the way)
            sys.stdout.write("\033[F\033[K" * 8)
            sys.stdout.flush()
 
            print(f"\n{text}\n\nThese are the options you have:\n\n[ {' '.join(option)} ]\n")
            val = input("Choice: ").lower()
 
 
# =============================================================================
# DOWNLOAD ENGINE (WITH JS SUPPRESSION & TYPE HINTS)
# =============================================================================
def playlist_download(save_path:str, **kwargs)-> None:
    """Enable Playlist Downloading option"""
 
    print_space()
 
    confirm = request_loop("Do you want to download a whole playlist?", ["yes", "no"])
 
    if confirm == "yes":
        print_space()
        url:str = input("Enter the url: ")
 
        print_space()
 
        playlist_format:str = request_loop("What format will you like your file to be in", ["audio", "video", "both"])
 
        if playlist_format == "both":
            process_download('%(title)s', url, "audio", save_path)
            process_download('%(title)s', url, "video", save_path)  
        else:
            process_download('%(title)s', url, playlist_format, save_path)            
    else:
        print_space()  
        print("Okay,👌👌")          
 
def progress_hook(d):  # Used AI
    if d['status'] == 'downloading':
        # Create a custom long bar without the extra 'stats' 
        if not hasattr(progress_hook, 'pbar'):
            progress_hook.pbar = tqdm(
                total=100, 
                desc="Progress", 
                unit="%",
                ncols=40, # This makes the bar longer (adjust as needed)
                bar_format="{desc}: |{bar}| {percentage:3.0f}%" # Removes ETA/Speed
            )
 
        raw_percent = d.get('_percent_str', '0%')
        clean_percent = clean_ansi(raw_percent).replace('%', '').strip()
 
        try:
            progress_hook.pbar.n = float(clean_percent)
            progress_hook.pbar.refresh()
        except ValueError:
            pass
 
    elif d['status'] == 'finished':
        if hasattr(progress_hook, 'pbar'):
            progress_hook.pbar.close()
            delattr(progress_hook, 'pbar')
 
 
def process_download(output_name: str, url: str, media_format: str, full_path: str) -> None:
    """
    Handles yt-dlp logic with flags to ignore JS runtime warnings.
    Simply put; downloads the whole file.
 
    """
 
    common_opts = {
        "outtmpl": f"{full_path}/{output_name}.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "noprogress": True,
        "cachedir": False,
        "progress_hooks": [progress_hook],
    }
 
    # Selection logic using a dictionary for cleaner PEP 8 style
    if media_format == "video":
        opts = {
            **common_opts,
            "format": "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4"
        }
    elif media_format == "audio":
        opts = {**common_opts, "format": "bestaudio[ext=m4a]/best"}
    else:
        opts = {
            **common_opts,
            "format": "bestaudio[ext=m4a]/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        }
 
    with YoutubeDL(opts) as ydl:
        ydl.download([url])
 
# =============================================================================
# VALIDATION LOGIC
# =============================================================================
 
def get_validated_format() -> str:
    """Asks for format and cleans screen on error with a delay."""
    media_options: List[str] = ["video", "audio", "extract"]
 
    print_space()
 
    choice: str = input("Choose Format: ").lower().strip()
 
    print_space()
 
    while True:
        if choice not in media_options:
            print_space()
            print(f"❌ '{choice}' is not a valid option!")
            time.sleep(2)
 
            # Clean up the 3 lines (Error, Space, and Input)
            for _ in range(3):
                erase_previous_line()
 
            print("⚠️ Please enter a valid choice:")
 
            print_space()
 
            print(f"Options: {', '.join(media_options)}")
 
            print_space() 
 
            choice = input("Choose Format: ").lower().strip()
        else:
            break
    return choice
 
# =============================================================================
# MAIN SYSTEM START
# =============================================================================
 
clear_screen()
print("-------- YouTube Downloader (YDL) -------")
print_space()
 
# --- Segment: Path Verification ---
try:
    with open("path.txt", "r") as f:
        save_path: str = f.read().strip()
except FileNotFoundError:
    save_path = "NOT_SET"
 
while True:
    if not os.path.exists(save_path) or save_path == "NOT_SET":
        print(f"❌ Path Error: '{save_path}' does not exist.")
        print_space()
        save_path = input("Enter a correct path: ").strip()
 
        time.sleep(2) 
        for _ in range(3):
            erase_previous_line()
    else:
        break
 
print_space()
print(f"✅ Target Directory: {save_path}")
print_space()
 
# --- Segment: Link Gathering (With Empty Input Protection) ---
print("--- Step 1: Link Selection ---")
print_space()
file_type: str = input("Is it a single, double file or a playlist: ").lower().strip()
links: List[str] = []
 
if file_type == "single":
    print_space()
    raw_url: str = input("Enter the URL: ").strip()
    if raw_url:
        links.append(raw_url)
elif file_type == "double":
    print_space()
    print("(Type 'done' when finished)")
    while True:
        url_input: str = input("Enter link: ").strip()
        if url_input.lower() == 'done':
            break
        if not url_input:  # Safety check: skip empty enters
            erase_previous_line()
            continue
        links.append(url_input)
elif file_type == "playlist":
     playlist_download(save_path)      
 
# --- Segment: Processing Loop ---
try:
    for link in links:
        print_space()
        print("🔃 Fetching details...")
 
        with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(link, download=False)
            title = info.get('title', 'Unknown Title')
 
        print_space()
        print(f"📖 Found: {title}")
        print_space()
 
        both: str = input("Download both Video and Audio? (yes/no): ").lower().strip()
 
        if both == "no":
            print_space()
            name: str = input("Save as (Filename): ").strip()
            fmt: str = get_validated_format()
 
            print_space()
            print(f"🚀 Downloading {fmt}...")
            process_download(name, link, fmt, save_path)
        else:
            print_space()
            name: str = input("Save as (Filename): ").strip()
 
            print("🚀 Downloading Audio & Video...")
            process_download(name, link, "audio", save_path)
            process_download(name, link, "video", save_path)
 
    print_space()
    print("Done! All files processed successfully. ✅")
    print_space()
 
except Exception as e:
    print_space()
    print(f"⚠️ System Error: {e}")        status_text
    )

ft.app(target=main)
