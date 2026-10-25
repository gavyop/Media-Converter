# 🎧 MP4 to Separate MP3 Tracks — Windows App

A small offline Windows desktop app that extracts **each embedded audio track** from an MP4 into a separate **320 kbps MP3**. For example, a video with two audio streams gives you `Track_1.mp3` and `Track_2.mp3`, ready for your video editor.

## Features
- Simple window: **Choose MP4**, select the file, export automatically.
- Extracts multiple audio streams independently (not mixed together).
- Also accepts `.mkv`, `.mov` and `.m4v` video files.
- Creates an output directory alongside the video, named `<video_name>_MP3_Tracks`.
- Never overwrites an earlier output directory and does not modify the original video.
- Works entirely on your computer; no uploads.

## Requirements
- Windows 10/11
- **Python 3** with Tkinter (usually included in the normal Windows Python installer): https://www.python.org/downloads/windows/
- **FFmpeg**: https://ffmpeg.org/download.html — a Windows build with `ffmpeg.exe` (and ideally `ffprobe.exe`).

FFmpeg is not bundled with this repository. Put `ffmpeg.exe` next to `START_HERE.bat`, add FFmpeg's `bin` folder to your Windows `PATH`, or select `ffmpeg.exe` when the app asks.

## How to run
1. Download this repository as ZIP and extract it.
2. Double-click **`START_HERE.bat`**.
3. Choose your MP4 in the file picker.
4. Wait until the app says **DONE**, then click **Open MP3 Folder**.

**Example output:**
```
Holiday_Video.mp4
Holiday_Video_MP3_Tracks/
  Track_1.mp3
  Track_2.mp3
```

## How it works
The script uses `ffprobe` (or FFmpeg fallback) to count streams and extracts stream `0:a:0`, `0:a:1`, and so on, encoding each separately with `libmp3lame` at 320 kbps.

**Note:** Converting to MP3 does **not** increase the original audio quality. MP3 is a lossy format.

## Safety and privacy
- Everything runs locally; no accounts, network requests or API keys.
- **Do not commit personal recordings or exported audio to GitHub.** `.gitignore` excludes common media types.
- Never include private passwords/tokens in a repository, even if it's private.

## Testing
On any machine with FFmpeg and Python available:
```
python -m unittest discover -s tests -v
```
The test includes an optional end-to-end extraction if `ffmpeg`/`ffprobe` are installed.

## Project files
- `FFmpeg_Track_Extractor.pyw` — Tkinter GUI.
- `converter_core.py` — FFmpeg extraction logic.
- `START_HERE.bat` — Windows launcher.
- `README_GR.txt` — short Greeklish usage instructions.
- `tests/` — tests.

**Status:** Personal project / Windows utility. This project is not affiliated with FFmpeg.
