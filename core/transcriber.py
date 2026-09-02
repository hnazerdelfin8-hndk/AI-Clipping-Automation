import os
from groq import Groq

def transcribe(path):
    key=os.getenv('GROQ_API_KEY')
    if not key: raise RuntimeError('GROQ_API_KEY is missing. Put it in .env.')
    client=Groq(api_key=key)
    with open(path,'rb') as f:
        r=client.audio.transcriptions.create(file=(os.path.basename(path),f.read()), model=os.getenv('GROQ_WHISPER_MODEL','whisper-large-v3-turbo'), response_format='verbose_json', timestamp_granularities=['segment'])
    return {'text':r.text,'segments':[{'start':s.start,'end':s.end,'text':s.text.strip()} for s in r.segments]}
