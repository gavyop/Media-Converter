"""Testable FFmpeg commands for the Media Converter Windows GUI."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

VIDEO_FORMATS = ('mp4', 'mkv', 'mov', 'webm', 'avi')
AUDIO_FORMATS = ('mp3', 'flac', 'wav', 'm4a', 'aac', 'ogg', 'opus')
MODES = ('Extract audio tracks', 'Convert audio', 'Convert video')
MEDIA_INPUT_EXTENSIONS = {'.mp4', '.mkv', '.mov', '.webm', '.avi', '.mp3', '.flac', '.wav', '.aac', '.m4a', '.ogg', '.opus'}


def locate_tools(base: Path, ffmpeg_override: str | None = None) -> tuple[str, str] | None:
    """Return FFmpeg/FFprobe pair, prioritizing selected file, local pair, then PATH."""
    if ffmpeg_override:
        selected = Path(ffmpeg_override)
        probe = selected.with_name('ffprobe.exe' if selected.suffix.lower() == '.exe' else 'ffprobe')
        if selected.is_file() and probe.is_file():
            return str(selected), str(probe)
        return None
    candidates = []
    base = Path(base)
    candidates.append(base / 'ffmpeg.exe')
    candidates.append(base / 'ffmpeg')
    for exe in candidates:
        if exe.is_file():
            probe = exe.with_name('ffprobe.exe' if exe.suffix.lower() == '.exe' else 'ffprobe')
            if probe.is_file():
                return str(exe), str(probe)
    ffmpeg_path, ffprobe_path = shutil.which('ffmpeg'), shutil.which('ffprobe')
    return (ffmpeg_path, ffprobe_path) if ffmpeg_path and ffprobe_path else None


def streams_for(src: Path, ffprobe: str) -> list[dict]:
    args = [str(ffprobe), '-v', 'error', '-show_entries', 'stream=index,codec_type', '-of', 'json', str(src)]
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError('FFprobe could not read this file:\n' + result.stderr[-1500:])
    try:
        return json.loads(result.stdout)['streams']
    except (json.JSONDecodeError, KeyError) as exc:
        raise RuntimeError('FFprobe returned invalid stream information.') from exc


def unique_output(directory: Path, stem: str, extension: str) -> Path:
    dest = directory / f'{stem}.{extension}'
    index = 2
    while dest.exists():
        dest = directory / f'{stem}_{index}.{extension}'
        index += 1
    return dest


def build_command(ffmpeg: str, src: Path, dest: Path, mode: str, fmt: str, audio_index: int = 0) -> list[str]:
    if mode not in MODES:
        raise ValueError('Unknown operation.')
    valid = VIDEO_FORMATS if mode == 'Convert video' else AUDIO_FORMATS
    if fmt not in valid:
        raise ValueError(f'Invalid format {fmt!r} for {mode}.')

    cmd = [str(ffmpeg), '-hide_banner', '-nostdin', '-n', '-i', str(src)]
    if mode == 'Extract audio tracks':
        cmd += ['-map', f'0:a:{audio_index}', '-vn', '-sn', '-dn']
    elif mode == 'Convert audio':
        cmd += ['-map', '0:a:0', '-vn', '-sn', '-dn']
    else:
        cmd += ['-map', '0:v:0', '-map', '0:a?', '-sn', '-dn']

    audio_encoders = {
        'mp3': ['-c:a', 'libmp3lame', '-b:a', '320k'],
        'flac': ['-c:a', 'flac'],
        'wav': ['-c:a', 'pcm_s16le'],
        'm4a': ['-c:a', 'aac', '-b:a', '256k'],
        'aac': ['-c:a', 'aac', '-b:a', '256k', '-f', 'adts'],
        'ogg': ['-c:a', 'libvorbis', '-q:a', '6'],
        'opus': ['-c:a', 'libopus', '-b:a', '192k'],
    }
    video_encoders = {
        'mp4': ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k'],
        'mkv': ['-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k'],
        'mov': ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k'],
        'webm': ['-c:v', 'libvpx-vp9', '-b:v', '1M', '-c:a', 'libopus', '-b:a', '128k'],
        'avi': ['-c:v', 'mpeg4', '-q:v', '4', '-c:a', 'libmp3lame', '-b:a', '192k'],
    }
    cmd += video_encoders[fmt] if mode == 'Convert video' else audio_encoders[fmt]
    return cmd + [str(dest)]


def run_conversion(src: Path, mode: str, fmt: str, ffmpeg: str, ffprobe: str) -> list[Path]:
    """Convert with no overwrite, and delete only an incomplete output on FFmpeg errors."""
    src = Path(src).resolve()
    if not src.is_file():
        raise FileNotFoundError(f'Selected file does not exist: {src}')
    info = streams_for(src, ffprobe)
    audio_count = sum(s.get('codec_type') == 'audio' for s in info)
    video_count = sum(s.get('codec_type') == 'video' for s in info)
    if mode == 'Convert video' and not video_count:
        raise ValueError('This file has no video track.')
    if mode != 'Convert video' and not audio_count:
        raise ValueError('This file has no audio track.')
    if mode not in MODES:
        raise ValueError('Unknown conversion operation.')
    count = audio_count if mode == 'Extract audio tracks' else 1
    outputs = []
    for index in range(count):
        name = src.stem + (f'_track_{index + 1}' if mode == 'Extract audio tracks' else '_converted')
        dest = unique_output(src.parent, name, fmt)
        command = build_command(ffmpeg, src, dest, mode, fmt, index)
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if result.returncode:
                raise RuntimeError(f'FFmpeg error for track {index + 1}:\n{result.stderr[-2400:]}')
            if not dest.is_file() or dest.stat().st_size == 0:
                raise RuntimeError('FFmpeg did not create a valid output file.')
        except Exception:
            if dest.exists():
                try:
                    dest.unlink()
                except OSError:
                    pass
            raise
        outputs.append(dest)
    return outputs
