import subprocess
from pathlib import Path


def render_clip(src, start, end, ass, out):
    start = max(0.0, float(start))
    end = float(end)
    duration = end - start
    if duration <= 0:
        raise ValueError("Clip end must be greater than start.")

    subtitle_file = str(Path(ass).resolve()).replace("\\", "/").replace("'", "\\'")
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,"
        f"subtitles='{subtitle_file}'"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(start), "-i", str(src), "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
        str(out),
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError("FFmpeg failed: " + result.stderr[-2000:])
    if not Path(out).exists() or Path(out).stat().st_size == 0:
        raise RuntimeError("FFmpeg produced an empty output file.")
