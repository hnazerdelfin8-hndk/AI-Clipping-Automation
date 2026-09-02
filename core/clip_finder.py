import json
import os

from groq import Groq


def _clamp_moments(moments, max_time):
    clean = []
    for item in moments:
        try:
            start = max(0.0, min(float(item["start"]), max_time))
            end = max(0.0, min(float(item["end"]), max_time))
        except (KeyError, TypeError, ValueError):
            continue
        if end <= start:
            continue
        if end - start < 8:
            continue
        clean.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "title": str(item.get("title", "AI Clip"))[:120],
            "hook": str(item.get("hook", ""))[:240],
            "score": max(0, min(100, int(float(item.get("score", 0))))),
            "reason": str(item.get("reason", ""))[:300],
        })
    return sorted(clean, key=lambda x: x["score"], reverse=True)[:5]


def find_moments(transcript):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is missing.")

    segments = transcript.get("segments", [])
    max_time = max((float(s.get("end", 0)) for s in segments), default=0.0)
    if max_time <= 0 or not transcript.get("text", "").strip():
        raise RuntimeError("No usable transcript was produced.")

    client = Groq(api_key=key)
    payload = json.dumps({"text": transcript["text"], "segments": segments}, ensure_ascii=False)
    prompt = """You are an expert short-form video editor. Find the strongest 3-5 moments from this transcript. Prefer moments with a strong hook, surprise, emotion, useful insight, conflict, humor, or clear payoff. Target 15-60 seconds when possible. Start and end on natural sentence boundaries. Return ONLY a JSON object with a clips array. Each item must contain: start (number), end (number), title (string), hook (string), score (0-100), reason (string). Keep timestamps inside the transcript range and never invent content."""

    result = client.chat.completions.create(
        model=os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile"),
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": payload},
        ],
    )
    obj = json.loads(result.choices[0].message.content)
    moments = obj.get("clips", [])
    if not isinstance(moments, list):
        raise RuntimeError("AI returned an invalid clip list.")
    clean = _clamp_moments(moments, max_time)
    if not clean:
        raise RuntimeError("AI did not return any usable clip moments.")
    return clean
