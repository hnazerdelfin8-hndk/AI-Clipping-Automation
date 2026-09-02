import os
from pathlib import Path

from groq import Groq


def transcribe(path):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to the Codespace environment or .env.")

    model = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")
    client = Groq(api_key=key)
    file_path = Path(path)

    with file_path.open("rb") as f:
        result = client.audio.transcriptions.create(
            file=(file_path.name, f.read()),
            model=model,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    segments = []
    for segment in getattr(result, "segments", []) or []:
        segments.append({
            "start": float(segment.start),
            "end": float(segment.end),
            "text": str(segment.text).strip(),
        })

    return {"text": result.text, "segments": segments}
