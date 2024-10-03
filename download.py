import json
import os
import subprocess
import sys
import tempfile
import time
import zipfile

import requests

from helpers.config import create_config, read_config, save_config
from helpers.github import auto_update
from helpers.print_colored import (
    CYAN,
    GREEN,
    RED,
    WHITE,
    print_colored,
    print_colored_bold,
)

REPO = "SavageCore/BSPlaylistDownloader"
CURRENT_VERSION = "0.0.0"
APP_PATH = os.path.dirname(os.path.abspath(sys.executable))

print("\033[H\033[J")
print_colored_bold(f"\nBSPlaylistDownloader ({CURRENT_VERSION})", GREEN)
print("-" * 40)


def download_songs(songs):
    for s in songs:
        # Skip songs that are already downloaded
        if os.path.exists(f"songs/{s['map']['id']}.zip"):
            continue

        url = "https://api.beatsaver.com/download/key/" + s["map"]["id"]
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(f"songs/{s['map']['id']}.zip", "wb") as f:
                f.write(response.content)
        else:
            print(f"Failed to download {url}: {response.status_code}")


if not read_config():
    create_config()

config = read_config()

auto_update(REPO, CURRENT_VERSION, APP_PATH, config)

# Define the User-Agent to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

legacy_playlist = False


def run_adb_command(command, retries=3, timeout=10):
    for _ in range(retries):
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout.decode(), stderr.decode()
        except subprocess.TimeoutExpired:
            process.kill()
            time.sleep(1)
    return None, None


try:
    # Ensure the 'songs' directory exists
    if not os.path.exists("songs"):
        os.makedirs("songs")

    if len(sys.argv) > 1:
        playlist_id = sys.argv[1]
        if playlist_id.isdigit():
            pass
        elif not playlist_id.isdigit() and "/" in playlist_id:
            playlist_id = playlist_id.split("/")[-1]
        else:
            print_colored(f"Opening playlist {playlist_id}", CYAN)
            # Load bplist file, extract playlist ID
            with open(playlist_id, "r") as f:
                playlist = json.load(f)
                if "customData" in playlist and "syncURL" in playlist["customData"]:
                    playlist_id = playlist["customData"]["syncURL"].split("/")[-2]
                else:
                    songs = playlist["songs"]
                    print(f"Downloading {len(songs)} songs from legacy playlist")

                    # Map the songs to the new format
                    songs = [
                        {
                            "map": {
                                "id": song["key"],
                                "name": song["songName"],
                                "hash": song["hash"],
                            }
                        }
                        for song in songs
                    ]

                    download_songs(songs)

                    legacy_playlist = True

    else:
        if "playlist_id" in config:
            playlist_id = config["playlist_id"]
        else:
            print_colored_bold("Please provide a playlist URL: ", WHITE)
            playlist_url = input("")
            playlist_id = playlist_url.split("/")[-1]
            # Clear the screen
            os.system("cls" if os.name == "nt" else "clear")

    if not legacy_playlist:
        # Save the playlist_id to the config file
        config["playlist_id"] = playlist_id
        save_config(config)

        url = f"https://api.beatsaver.com/playlists/id/{playlist_id}/0"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            playlist = json.loads(response.text)
            songs = playlist["maps"]
            totalMaps = playlist["playlist"]["stats"]["totalMaps"]
            playlistName = playlist["playlist"]["name"]

            if totalMaps > 100:
                total_pages = (totalMaps + 99) // 100  # Calculate total number of pages
                for i in range(1, total_pages):
                    url = f"https://api.beatsaver.com/playlists/id/{playlist_id}/{i}"
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        songs += json.loads(response.text)["maps"]
                    else:
                        print_colored(
                            f"Failed to get playlist {url}: {response.status_code}", RED
                        )

            print(f"Downloading {len(songs)} songs from {playlistName} [{playlist_id}]")

            download_songs(songs)
        else:
            print_colored(f"Failed to get playlist {url}: {response.status_code}", RED)

except Exception as e:
    print(f"An error occurred: {e}")

print("")

print_colored_bold("Would you like to install the songs? (Y/n): ", WHITE)
install = input("")
if install.lower() == "y" or install == "":
    print("Finding Quest...")
    # Check adb for devices
    stdout, stderr = run_adb_command(["adb", "devices"])
    if stdout:
        devices = stdout.splitlines()
        if len(devices) > 2:
            print("Quest found. Installing songs...")

            # Get all songs already installed
            adb_ls_command = "adb shell ls /sdcard/ModData/com.beatgames.beatsaber/Mods/SongCore/CustomLevels/"
            stdout, stderr = run_adb_command(adb_ls_command.split())
            installed_songs = stdout.splitlines()

            for file in os.listdir("songs"):
                if file.endswith(".zip"):
                    song_id = file.split(".")[0]
                    with zipfile.ZipFile(f"songs/{file}", "r") as zip_ref:
                        temp_dir = tempfile.mkdtemp()
                        zip_ref.extractall(temp_dir)
                        if f"{song_id}" not in installed_songs:
                            print("")
                            print(f"Installing {song_id}...")
                            adb_push_command = f"adb push {temp_dir} /sdcard/ModData/com.beatgames.beatsaber/Mods/SongCore/CustomLevels/{song_id}"
                            with open(os.devnull, "w") as devnull:
                                subprocess.Popen(
                                    adb_push_command.split(),
                                    stdout=devnull,
                                    stderr=devnull,
                                )
                            print(f"Installed {song_id}")
        else:
            print_colored(
                "No devices found. Please connect your Quest and try again.", RED
            )

        run_adb_command(["adb", "kill-server"])
    else:
        print_colored("Failed to run adb devices command.", RED)

print("")
print("Done!")
print("")
print_colored_bold("Press Enter to exit...", WHITE)
input("")
