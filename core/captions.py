from pathlib import Path

def ts(sec):
    sec=max(0,float(sec)); h=int(sec//3600); m=int((sec%3600)//60); s=sec%60
    return f'{h}:{m:02d}:{s:05.2f}'.replace('.',',')

def write_ass(transcript,start,end,path):
    lines=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','','[V4+ Styles]','Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding','Style: Default,Arial,52,&H00FFFFFF,&H000000FF,&H80000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,60,60,260,1','','[Events]','Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text']
    for seg in transcript['segments']:
        a=max(float(seg['start']),float(start)); b=min(float(seg['end']),float(end))
        if b<=a: continue
        text=str(seg['text']).replace('{','(').replace('}',')').replace('\n',' ')
        lines.append(f'Dialogue: 0,{ts(a-float(start))[:-1]},{ts(b-float(start))[:-1]},Default,,0,0,0,,{text}')
    Path(path).write_text('\n'.join(lines),encoding='utf-8')
