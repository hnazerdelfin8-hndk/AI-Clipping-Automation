import json
import os

from groq import Groq


def _clamp_moments(moments, max_time):
    clean = []
    seen = set()
    for item in moments:
        try:
            start = max(0.0, min(float(item["start"]), max_time))
            end = max(0.0, min(float(item["end"]), max_time))
        except (KeyError, TypeError, ValueError):
            continue
        duration = end - start
        if duration < 10 or duration > 60 or end <= start:
            continue
        key = (round(start, 1), round(end, 1))
        if key in seen:
            continue
        seen.add(key)
        clean.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "title": str(item.get("title", "AI Clip")).strip()[:120],
            "hook": str(item.get("hook", "")).strip()[:240],
            "score": max(0, min(100, int(float(item.get("score", 0))))),
            "reason": str(item.get("reason", "")).strip()[:300],
        })
    return sorted(clean, key=lambda x: x["score"], reverse=True)[:5]


def find_moments(transcript):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is missing.")

    segments = transcript.get("segments", [])
    max_time = max((float(s.get("end", 0)) for s in segments), default=0.0)
    text = str(transcript.get("text", "")).strip()
    if max_time <= 0 or not text:
        raise RuntimeError("No usable transcript was produced.")

    client = Groq(api_key=key)
    payload = json.dumps({"text": text, "segments": segments}, ensure_ascii=False)
    prompt = """You are an expert short-form video editor. Find the strongest 3-5 moments from this transcript. Prefer strong hooks, surprise, emotion, useful insight, conflict, humor, or a clear payoff. Each clip MUST be 10-60 seconds. Start and end on natural sentence boundaries. Do not overlap clips. Use only timestamps present in the transcript. Return ONLY a JSON object: {\"clips\":[{\"start\":number,\"end\":number,\"title\":string,\"hook\":string,\"score\":number,\"reason\":string}]}."""

    result = client.chat.completions.create(
        model=os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile"),
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": payload},
        ],
    )
    content = result.choices[0].message.content or "{}"
    try:
        obj = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"AI returned invalid JSON: {exc}") from exc

    moments = obj.get("clips", [])
    if not isinstance(moments, list):
        raise RuntimeError("AI returned an invalid clip list.")
    clean = _clamp_moments(moments, max_time)
    if not clean:
        raise RuntimeError("AI did not return any usable 10-60 second clip moments.")
    return clean
