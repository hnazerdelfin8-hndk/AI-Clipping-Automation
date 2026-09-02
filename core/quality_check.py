import json
import shutil
import subprocess
from pathlib import Path


def check_video(path):
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return {"ok": False, "error": "Output file is missing or empty."}
    if shutil.which("ffprobe") is None:
        return {"ok": False, "error": "ffprobe is not installed."}

    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height,duration", "-of", "json", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"ok": False, "error": "ffprobe failed", "details": result.stderr[-800:]}

    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": "ffprobe returned invalid JSON."}

    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not video:
        return {"ok": False, "error": "No video stream found."}

    width = video.get("width")
    height = video.get("height")
    duration = float(video.get("duration") or data.get("format", {}).get("duration") or 0)
    size = int(data.get("format", {}).get("size") or path.stat().st_size)
    checks = {
        "resolution": width == 1080 and height == 1920,
        "duration": duration > 0,
        "size": size > 10000,
        "video_codec": video.get("codec_name") == "h264",
        "audio": audio is not None,
    }
    return {
        "ok": all(checks.values()),
        "width": width,
        "height": height,
        "duration": round(duration, 2),
        "size_bytes": size,
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name") if audio else None,
        "checks": checks,
    }
