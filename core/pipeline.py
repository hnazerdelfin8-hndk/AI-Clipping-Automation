import json
import traceback
from pathlib import Path

from .captions import write_ass
from .clip_finder import find_moments
from .clip_generator import render_clip
from .quality_check import check_video
from .transcriber import transcribe


def process_video(source, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        transcript = transcribe(source)
        (out / "transcript.json").write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")

        moments = find_moments(transcript)
        (out / "moments.json").write_text(json.dumps(moments, ensure_ascii=False, indent=2), encoding="utf-8")

        results = []
        for index, moment in enumerate(moments, 1):
            start = float(moment["start"])
            end = min(float(moment["end"]), start + 60.0)
            if end <= start:
                continue

            ass = out / f"clip_{index:02d}.ass"
            clip = out / f"clip_{index:02d}.mp4"
            write_ass(transcript, start, end, ass)
            render_clip(source, start, end, ass, clip)
            qa = check_video(clip)
            results.append({
                "file": clip.name,
                "title": moment.get("title", "AI Clip"),
                "hook": moment.get("hook", ""),
                "score": moment.get("score", 0),
                "reason": moment.get("reason", ""),
                "start": start,
                "end": end,
                "qa": qa,
            })

        if not results:
            raise RuntimeError("No clips were successfully rendered.")
        if not any(item["qa"].get("ok") for item in results):
            raise RuntimeError("QA rejected every rendered clip.")

        (out / "done.json").write_text(json.dumps({"clips": results}, ensure_ascii=False, indent=2), encoding="utf-8")
        return results
    except Exception as exc:
        (out / "error.json").write_text(json.dumps({"error": str(exc), "traceback": traceback.format_exc()}, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
