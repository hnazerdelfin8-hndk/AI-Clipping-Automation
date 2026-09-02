import json
import traceback
from pathlib import Path

from .captions import write_ass
from .clip_finder import find_moments
from .clip_generator import render_clip
from .quality_check import check_video
from .transcriber import transcribe


def _write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def process_video(source, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        transcript = transcribe(source)
        _write_json(out / "transcript.json", transcript)

        moments = find_moments(transcript)
        _write_json(out / "moments.json", {"clips": moments})

        results = []
        failures = []
        for index, moment in enumerate(moments, 1):
            try:
                start = max(0.0, float(moment["start"]))
                end = min(float(moment["end"]), start + 60.0)
                if end <= start or end - start < 10:
                    raise ValueError("Clip duration must be between 10 and 60 seconds.")

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
                    "duration": round(end - start, 2),
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
