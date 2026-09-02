import json, traceback
from pathlib import Path
from .transcriber import transcribe
from .clip_finder import find_moments
from .clip_generator import render_clip
from .captions import write_ass
from .quality_check import check_video

def process_video(source, out_dir):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    try:
        transcript=transcribe(source)
        (out/'transcript.json').write_text(json.dumps(transcript,ensure_ascii=False,indent=2))
        moments=find_moments(transcript)
        (out/'moments.json').write_text(json.dumps(moments,ensure_ascii=False,indent=2))
        results=[]
        for i,m in enumerate(moments,1):
            start=float(m['start']); end=float(m['end'])
            if end <= start: continue
            ass=out/f'clip_{i:02d}.ass'
            write_ass(transcript,start,end,ass)
            clip=out/f'clip_{i:02d}.mp4'
            render_clip(source,start,end,ass,clip)
            results.append({'file':clip.name,'title':m.get('title','AI Clip'),'hook':m.get('hook',''),'score':m.get('score',0),'qa':check_video(clip)})
        (out/'done.json').write_text(json.dumps({'clips':results},ensure_ascii=False,indent=2))
    except Exception as e:
        (out/'error.json').write_text(json.dumps({'error':str(e),'traceback':traceback.format_exc()},indent=2))
