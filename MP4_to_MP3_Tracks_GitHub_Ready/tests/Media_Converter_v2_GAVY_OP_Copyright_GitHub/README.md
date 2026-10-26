# Media Converter v2 — GAVY_OP

**Copyright © 2026 GAVY_OP. All rights reserved.**

GitHub: https://github.com/gavyop  
Repository: https://github.com/gavyop/MP4-to-MP3-Track-Extractor (**Private**)

A small Windows Python + FFmpeg app with a **Choose File** dialog.

## Features
- Extract each audio track from a video as a separate file.
- Audio outputs: MP3 (320 kbps), FLAC, WAV, M4A, AAC, OGG, Opus.
- Video conversion: MP4, MKV, MOV, WEBM, AVI.
- Audio conversion: MP3, FLAC, WAV, M4A, AAC, OGG, Opus.
- Does not overwrite existing output files.
- If FFmpeg is missing, browse to `ffmpeg.exe` (with `ffprobe.exe` beside it).
- Visible copyright notice and clickable **GAVY_OP on GitHub** / **Project repository** links.

## Windows setup
1. Install Python 3 with Tkinter.
2. Install FFmpeg **and FFprobe** from a trusted distribution.
3. Unzip this repository and double-click `START_HERE.bat`.
4. Click **Choose File**, choose an operation and an output format, then **Convert / Extract**.
5. If requested, select `ffmpeg.exe` in the FFmpeg `bin` folder.

The output is saved beside the source file. For example `video.mp4` with two audio tracks can produce `video_track_1.mp3` and `video_track_2.mp3`.

## v2 changes
- Video and audio format conversion and multi-track audio extraction.
- Built-in FFmpeg/FFprobe file selection when unavailable from PATH.
- Better error messages, cleanup of incomplete files, and protection from concurrent conversions.
- Added **GAVY_OP copyright** and **clickable GitHub links**.
- The displayed version is consistently **v2**.

## Notes
- MP3 to FLAC conversion does **not** restore lost audio quality.
- Video conversion can be slower and may re-encode footage.
- Conversion functions have been tested with FFmpeg on Linux; Windows GUI use still needs verification on your Windows PC.
