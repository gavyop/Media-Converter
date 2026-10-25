"""MP4 multi-audio-track -> individual MP3 files using FFmpeg.

No third-party Python dependencies; tested with Python 3.13 and FFmpeg 7.1.5.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import os
from pathlib import Path
from typing import Callable


class ConversionError(Exception):
    """A user-facing conversion failure."""


def _startupinfo():
    if os.name == "nt":
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return info
    return None


def locate_ffmpeg(app_directory: Path) -> Path | None:
    """Find FFmpeg next to app, in typical subfolders, or on PATH."""
    name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    candidates = [app_directory / name, app_directory / "bin" / name]
    if os.name == "nt":
        candidates.extend([Path(r"C:\ffmpeg\bin\ffmpeg.exe"), Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe")])
    for path in candidates:
        if path.is_file():
            return path
    found = shutil.which("ffmpeg")
    return Path(found) if found else None


def _find_ffprobe(ffmpeg: Path) -> Path | None:
    name = "ffprobe.exe" if os.name == "nt" else "ffprobe"
    sibling = ffmpeg.parent / name
    if sibling.is_file():
        return sibling
    found = shutil.which("ffprobe")
    return Path(found) if found else None


def audio_track_count(video_path: Path, ffmpeg: Path) -> int:
    """Use ffprobe JSON when present; fall back to FFmpeg's stream report."""
    probe = _find_ffprobe(ffmpeg)
    if probe:
        try:
            completed = subprocess.run([
                str(probe), "-v", "error", "-select_streams", "a",
                "-show_entries", "stream=index", "-of", "json", str(video_path)
            ], capture_output=True, text=True, timeout=60, startupinfo=_startupinfo())
            if completed.returncode == 0:
                data = json.loads(completed.stdout)
                return len(data.get("streams", []))
        except (OSError, ValueError, subprocess.TimeoutExpired):
            pass  # An FFmpeg-only installation still works.

    try:
        completed = subprocess.run([
            str(ffmpeg), "-hide_banner", "-i", str(video_path)
        ], capture_output=True, text=True, errors="replace", timeout=60,
            startupinfo=_startupinfo())
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ConversionError(f"Could not inspect the video: {exc}") from exc
    # Example: Stream #0:2[0x102](eng): Audio: aac ...
    return len(re.findall(r"^\s*Stream #0:\d+[^\r\n]*?: Audio:\s", completed.stderr, re.MULTILINE))


def make_output_directory(video_path: Path) -> Path:
    """Never overwrite an earlier extraction."""
    root = video_path.parent / f"{video_path.stem}_MP3_Tracks"
    candidate = root
    idx = 2
    while candidate.exists():
        candidate = video_path.parent / f"{video_path.stem}_MP3_Tracks_{idx}"
        idx += 1
    candidate.mkdir(parents=True)
    return candidate


def convert_all_tracks(
    video_path: Path,
    ffmpeg: Path,
    on_progress: Callable[[int, int], None] | None = None
) -> list[Path]:
    if not video_path.is_file():
        raise ConversionError("The selected video file was not found.")
    if not ffmpeg.is_file():
        raise ConversionError("FFmpeg executable not found.")

    count = audio_track_count(video_path, ffmpeg)
    if count == 0:
        raise ConversionError("No audio tracks were detected in this file.")
    if count > 30:
        raise ConversionError(f"Unexpected audio track count ({count}). Conversion cancelled.")

    directory = make_output_directory(video_path)
    outputs: list[Path] = []
    try:
        for idx in range(count):
            output = directory / f"Track_{idx + 1}.mp3"
            # `0:a:N` selects the N-th AUDIO stream, independent of video/subtitle order.
            args = [
                str(ffmpeg), "-hide_banner", "-loglevel", "error", "-nostdin",
                "-i", str(video_path), "-map", f"0:a:{idx}",
                "-vn", "-sn", "-dn", "-c:a", "libmp3lame",
                "-b:a", "320k", "-y", str(output)
            ]
            result = subprocess.run(
                args, capture_output=True, text=True, errors="replace",
                startupinfo=_startupinfo()
            )
            if result.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
                if output.exists():
                    output.unlink()
                message = result.stderr.strip()[-2500:] or "FFmpeg returned an error."
                raise ConversionError(f"Track {idx + 1} conversion failed:\n{message}")
            outputs.append(output)
            if on_progress:
                on_progress(idx + 1, count)
    except Exception:
        # Keep successful tracks for diagnosis rather than deleting user's conversions.
        raise
    return outputs
