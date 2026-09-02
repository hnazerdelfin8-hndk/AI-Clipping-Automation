import json
import subprocess
from pathlib import Path


def check_video(path):
    path = Path(path)
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,duration", "-of", "json", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"ok": False, "error": "ffprobe failed", "details": result.stderr[-500:]}

    data = json.loads(result.stdout or "{}")
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video:
        return {"ok": False, "error": "No video stream found."}

    width = video.get("width")
    height = video.get("height")
    duration = float(video.get("duration", 0) or 0)
    ok = width == 1080 and height == 1920 and duration > 0
    return {"ok": ok, "width": width, "height": height, "duration": round(duration, 2)}
