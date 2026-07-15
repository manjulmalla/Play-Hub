"""Utility helpers for video processing with FFmpeg and Pillow."""

import os
import subprocess

from django.conf import settings


def _ffmpeg_binary():
    """Return the configured or auto-detected FFmpeg executable name."""
    if getattr(settings, "FFMPEG_PATH", ""):
        return settings.FFMPEG_PATH
    return "ffmpeg"


def _ffprobe_binary():
    """Return the configured or auto-detected FFprobe executable name."""
    if getattr(settings, "FFMPEG_PATH", ""):
        # Allow overriding with the ffmpeg binary and derive ffprobe nearby.
        base = os.path.splitext(settings.FFMPEG_PATH)[0]
        return base + "-ffprobe" if os.path.exists(base + "-ffprobe") else "ffprobe"
    return "ffprobe"


def ffmpeg_available():
    """Check whether FFmpeg can be executed on this system."""
    try:
        subprocess.run(
            [_ffmpeg_binary(), "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def probe_metadata(video_path):
    """Return ``(duration, width, height)`` using ffprobe, or ``None``.

    Returns ``None`` when ffprobe is unavailable or the file cannot be read.
    """
    try:
        result = subprocess.run(
            [
                _ffprobe_binary(),
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,duration:format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
            text=True,
        )
        lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
        if len(lines) >= 3:
            duration = float(lines[2])
            width = int(lines[0])
            height = int(lines[1])
            return int(duration), width, height
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return None
    return None


def generate_thumbnail(video_path, output_path, timestamp=2):
    """Extract a single frame as a JPEG thumbnail using FFmpeg."""
    if not ffmpeg_available():
        return False
    try:
        subprocess.run(
            [
                _ffmpeg_binary(),
                "-y",
                "-ss",
                str(timestamp),
                "-i",
                video_path,
                "-vframes",
                "1",
                "-q:v",
                "2",
                output_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return os.path.exists(output_path)
    except (OSError, subprocess.SubprocessError):
        return False


def compress_video(input_path, output_path, height=720):
    """Re-encode a video to a web-friendly H.264/MP4 at the given height."""
    if not ffmpeg_available():
        return False
    try:
        subprocess.run(
            [
                _ffmpeg_binary(),
                "-y",
                "-i",
                input_path,
                "-vf",
                f"scale=-2:{height}",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-movflags",
                "+faststart",
                output_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return os.path.exists(output_path)
    except (OSError, subprocess.SubprocessError):
        return False


def generate_hls(input_path, output_dir):
    """Create an adaptive HLS playlist (master + variants) from a video.

    Returns the path to the master playlist or ``None`` when HLS cannot be
    generated (for example when FFmpeg is missing).
    """
    if not ffmpeg_available():
        return None
    try:
        os.makedirs(output_dir, exist_ok=True)
        master_path = os.path.join(output_dir, "master.m3u8")
        subprocess.run(
            [
                _ffmpeg_binary(),
                "-y",
                "-i",
                input_path,
                "-vf",
                "scale=-2:480",
                "-c:v",
                "libx264",
                "-b:v",
                "800k",
                "-c:a",
                "aac",
                "-f",
                "hls",
                "-hls_time",
                "6",
                "-hls_playlist_type",
                "vod",
                os.path.join(output_dir, "480p.m3u8"),
                "-vf",
                "scale=-2:720",
                "-c:v",
                "libx264",
                "-b:v",
                "1400k",
                "-c:a",
                "aac",
                "-f",
                "hls",
                "-hls_time",
                "6",
                "-hls_playlist_type",
                "vod",
                os.path.join(output_dir, "720p.m3u8"),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        # Build a simple master playlist pointing at the two variants.
        with open(master_path, "w", encoding="utf-8") as handle:
            handle.write("#EXTM3U\n")
            handle.write("#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=854x480\n")
            handle.write("480p.m3u8\n")
            handle.write("#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=1280x720\n")
            handle.write("720p.m3u8\n")
        return master_path
    except (OSError, subprocess.SubprocessError):
        return None
