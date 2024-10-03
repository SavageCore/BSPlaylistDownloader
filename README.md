# BSPlaylistDownloader

[![GitHub Build Status](https://img.shields.io/github/actions/workflow/status/SavageCore/BSPlaylistDownloader/build.yml?style=flat-square&logo=pytest)](https://github.com/SavageCore/BSPlaylistDownloader/actions/workflows/build.yml)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-black)](https://pypi.org/project/black/)

> A script to download all the songs from a playlist on [BeatSaver](https://beatsaver.com/). Optionally installs them to your Quest.

### Installation

You can find the latest releases [here](https://github.com/SavageCore/BSPlaylistDownloader/releases/latest/download/BSPlaylistDownloader-win64.exe).

Download `BSPlaylistDownloader-win64.exe` to a folder of your choice. A `songs` folder will be created in the same directory and store all the downloaded songs.

### Usage

Either Drag and Drop a `.bplist` playlist onto the executable or double click the executable and paste the playlist URL and press enter when prompted. [BeatSaver](https://beatsaver.com/playlists) and bsaber [bookmark backup](https://bookmarks.topc.at/) playlists are supported. On subsequent runs, unless you're Drag and Dropping a playlist or running via command line, the script will read the playlist url from the config file and download the songs without prompting.

Example url: `https://beatsaver.com/playlists/674833`

From the command line there are three ways to download a playlist:

1. By playlist ID, playlist URL or bplist file:

Note you'll want to enclose the file in quotes if it contains spaces. `BSPlaylistDownloader-win64.exe "C:\Users\Username\Downloads\BeatSaver - Bookmarks.bplist"`

```shell
.\BSPlaylistDownloader-win64.exe <playlist id or playlist url or bplist file>
```
