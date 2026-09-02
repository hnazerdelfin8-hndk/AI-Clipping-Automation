from pathlib import Path


def ass_ts(seconds):
    seconds = max(0.0, float(seconds))
    total_cs = round(seconds * 100)
    hours, rem = divmod(total_cs, 360000)
    minutes, rem = divmod(rem, 6000)
    secs, centis = divmod(rem, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def write_ass(transcript, start, end, path):
    header = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Default,Arial,52,&H00FFFFFF,&H00FFFFFF,&H80000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,60,60,260,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    events = []
    for seg in transcript.get("segments", []):
        a = max(float(seg.get("start", 0)), float(start))
        b = min(float(seg.get("end", 0)), float(end))
        if b <= a:
            continue
        text = str(seg.get("text", "")).strip().replace("{", "(").replace("}", ")").replace("\n", " ")
        if text:
            events.append(
                f"Dialogue: 0,{ass_ts(a - float(start))},{ass_ts(b - float(start))},Default,,0,0,0,,{text}"
            )

    Path(path).write_text("\n".join(header + events) + "\n", encoding="utf-8")
