import json
import subprocess
import traceback
from pathlib import Path

from .captions import write_ass
from .clip_finder import find_moments
from .clip_generator import render_clip
from .quality_check import check_video
from .transcriber import transcribe


def _write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _duration_seconds(source):
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", source,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def process_video(source, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        duration = _duration_seconds(source)
        transcript = transcribe(source)
        _write_json(out / "transcript.json", transcript)

        # Short uploads are already clips: do not run AI best-moment detection.
        if duration <= 60:
            moments = [{
                "start": 0.0,
                "end": duration,
                "title": "AI Clip",
                "hook": "",
                "score": 100,
                "reason": "Uploaded video is already 60 seconds or shorter.",
            }]
        else:
            moments = find_moments(transcript)

        # Best-moment clips must be at least 20 seconds and no more than 60 seconds.
        if duration > 60:
            moments = [m for m in moments if 20 <= float(m["end"]) - float(m["start"]) <= 60]

        _write_json(out / "moments.json", {"clips": moments, "source_duration": duration})

        results = []
        failures = []
        for index, moment in enumerate(moments, 1):
            try:
                start = max(0.0, float(moment["start"]))
                end = min(float(moment["end"]), start + 60.0, duration)
                clip_duration = end - start

                if duration > 60 and clip_duration < 20:
                    raise ValueError("AI clip duration must be between 20 and 60 seconds.")
                if duration <= 60 and clip_duration <= 0:
                    raise ValueError("Uploaded video has invalid duration.")

                ass = out / f"clip_{index:02d}.ass"
                clip = out / f"clip_{index:02d}.mp4"
                write_ass(transcript, start, end, ass)
                render_clip(source, start, end, ass, clip)
                qa = check_video(clip)
                item = {
                    "file": clip.name,
                    "title": moment.get("title", "AI Clip"),
                    "hook": moment.get("hook", ""),
                    "score": moment.get("score", 0),
                    "reason": moment.get("reason", ""),
                    "start": start,
                    "end": end,
                    "duration": round(clip_duration, 2),
                    "mode": "best_moment" if duration > 60 else "direct_clip",
                    "qa": qa,
                }
                if qa.get("ok"):
                    results.append(item)
                else:
                    failures.append({"clip": index, "error": "Quality check failed", "qa": qa})
            except Exception as exc:
                failures.append({"clip": index, "error": str(exc)})

        if not results:
            raise RuntimeError("No clips passed rendering and quality checks.")

        _write_json(out / "done.json", {"clips": results, "failed_clips": failures})
        return results
    except Exception as exc:
        _write_json(out / "error.json", {"error": str(exc), "traceback": traceback.format_exc()})
        raise
