import subprocess, json

def check_video(path):
    p=subprocess.run(['ffprobe','-v','error','-show_entries','stream=width,height,duration','-of','json',str(path)],capture_output=True,text=True)
    if p.returncode:
        return {'ok':False,'error':'ffprobe failed'}
    data=json.loads(p.stdout)
    video=next((s for s in data.get('streams',[]) if 'width' in s),None)
    ok=bool(video and video.get('width')==1080 and video.get('height')==1920)
    return {'ok':ok,'width':video.get('width') if video else None,'height':video.get('height') if video else None,'duration':video.get('duration') if video else None}
