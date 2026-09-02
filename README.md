# AI Clipping Automation — Phone-Friendly MVP

**Pipeline:** Video → Groq Whisper → AI moment finder → FFmpeg → 1080×1920 → captions → QA → downloads.

## 1. Open in GitHub Codespaces

Create a Codespace from the `main` branch, then open the terminal.

## 2. One-time setup

Run:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
pip install -r requirements.txt
```

Check:

```bash
ffmpeg -version
python --version
```

## 3. Add your Groq API key

For a quick test, create `.env` in the Codespace:

```env
GROQ_API_KEY=your_key_here
GROQ_WHISPER_MODEL=whisper-large-v3-turbo
GROQ_LLM_MODEL=llama-3.3-70b-versatile
MAX_UPLOAD_MB=500
```

**Never commit `.env` or paste your API key into GitHub source files.**

## 4. Start

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open the forwarded **port 8000** in the browser. Upload a short MP4 first (30–120 seconds is ideal for the first test).

## API

- `GET /api/health` — environment health check
- `POST /api/process` — upload and start a job
- `GET /api/jobs/{job_id}` — job status/results
- `GET /api/jobs/{job_id}/files` — generated MP4 list
- `GET /api/jobs/{job_id}/download/{filename}` — download a clip

## MVP notes

This is a Codespaces test MVP, not a production queue. FastAPI background tasks stop if the app/Codespace stops. Large videos and repeated processing consume compute and Groq API usage.

## Project structure

```text
AI-Clipping-Automation/
├── app.py
├── requirements.txt
├── .env.example
├── core/
│   ├── transcriber.py
│   ├── clip_finder.py
│   ├── captions.py
│   ├── clip_generator.py
│   ├── quality_check.py
│   └── pipeline.py
├── static/index.html
├── templates/default.json
├── tests/smoke_test.py
├── input/.gitkeep
└── output/.gitkeep
```
