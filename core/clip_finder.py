import os, json
from groq import Groq

def find_moments(transcript):
    key=os.getenv('GROQ_API_KEY')
    if not key: raise RuntimeError('GROQ_API_KEY is missing.')
    client=Groq(api_key=key)
    payload=json.dumps(transcript,ensure_ascii=False)
    prompt='''You are an expert short-form video editor. Find the strongest 3-5 moments from this transcript. Each clip should be 15-60 seconds when possible, have a clear hook/payoff, and avoid starting mid-sentence. Return ONLY a JSON object with a clips array. Each item: start (number), end (number), title (string), hook (string), score (0-100), reason (string). Keep timestamps inside transcript range.'''
    r=client.chat.completions.create(model=os.getenv('GROQ_LLM_MODEL','llama-3.3-70b-versatile'),temperature=0.2,response_format={'type':'json_object'},messages=[{'role':'system','content':prompt},{'role':'user','content':payload}])
    obj=json.loads(r.choices[0].message.content)
    moments=obj.get('clips',[])
    if not isinstance(moments,list): raise RuntimeError('AI returned invalid clip list.')
    return moments[:5]
