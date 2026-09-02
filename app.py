import os, uuid, json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from core.pipeline import process_video

BASE=Path(__file__).parent
INPUT=BASE/'input'; OUTPUT=BASE/'output'
INPUT.mkdir(exist_ok=True); OUTPUT.mkdir(exist_ok=True)
app=FastAPI(title='AI Clipping Automation MVP')
app.mount('/static', StaticFiles(directory=BASE/'static'), name='static')

@app.get('/')
def home(): return FileResponse(BASE/'static/index.html')

@app.post('/api/process')
async def process(background_tasks: BackgroundTasks, video: UploadFile=File(...)):
    if not video.filename.lower().endswith(('.mp4','.mov','.mkv','.webm')):
        raise HTTPException(400,'Upload a video file.')
    job=uuid.uuid4().hex[:12]
    src=INPUT/f'{job}_{Path(video.filename).name}'
    await video.seek(0)
    src.write_bytes(await video.read())
    background_tasks.add_task(process_video, str(src), str(OUTPUT/job))
    return {'job_id':job,'status':'queued','message':'Processing started.'}

@app.get('/api/jobs/{job_id}')
def status(job_id:str):
    d=OUTPUT/job_id
    if not d.exists(): return {'job_id':job_id,'status':'queued'}
    if (d/'error.json').exists(): return {'job_id':job_id,'status':'error',**json.loads((d/'error.json').read_text())}
    if (d/'done.json').exists():
        data=json.loads((d/'done.json').read_text()); data['status']='done'; return data
    return {'job_id':job_id,'status':'processing'}

@app.get('/api/jobs/{job_id}/files')
def files(job_id:str):
    d=OUTPUT/job_id
    if not d.exists(): raise HTTPException(404,'Job not found')
    return {'files':[p.name for p in d.glob('*.mp4')]}

@app.get('/api/jobs/{job_id}/download/{filename}')
def download(job_id:str, filename:str):
    p=(OUTPUT/job_id/filename).resolve()
    if p.parent != (OUTPUT/job_id).resolve() or p.suffix.lower()!='.mp4' or not p.exists(): raise HTTPException(404,'File not found')
    return FileResponse(p, media_type='video/mp4', filename=p.name)
