# AI Clipping Automation — Phone-Friendly MVP

**Pipeline:** Video → Groq Whisper → AI moment finder → FFmpeg → 1080×1920 → captions → QA → downloads.

## Quick start in GitHub Codespaces

This repository includes a Dev Container configuration. For a **new Codespace**, it automatically installs Python dependencies and FFmpeg.

For an **existing Codespace**, run once:

```bash
chmod +x setup.sh start.sh
./setup.sh
```

Then create `.env` from `.env.example` and add your Groq key. Never commit `.env`.

```bash
cp .env.example .env
nano .env
```

Set:

```env
GROQ_API_KEY=your_key_here
GROQ_WHISPER_MODEL=whisper-large-v3-turbo
GROQ_LLM_MODEL=llama-3.3-70b-versatile
MAX_UPLOAD_MB=500
```

Start the app:

```bash
chmod +x start.sh
./start.sh
```

Open forwarded **port 8000** in the Codespace browser. The dashboard has a system-health indicator. Upload a short MP4 (30–120 seconds is ideal for the first real test).

## Health check

Open `/api/health` or use the dashboard. It reports whether Groq is configured and whether FFmpeg/ffprobe are available.

## API

- `GET /api/health` — environment health check
- `POST /api/process` — upload and start a job
- `GET /api/jobs/{job_id}` — job status/results
- `GET /api/jobs/{job_id}/files` — generated MP4 list
- `GET /api/jobs/{job_id}/download/{filename}` — download a clip

## Pipeline behavior

1. Upload is streamed to disk with a configurable size limit.
2. Groq Whisper produces transcript segments with timestamps.
3. Groq LLM selects up to five 10–60 second moments.
4. FFmpeg creates 1080×1920 H.264/AAC clips and burns captions.
5. ffprobe validates resolution, duration, codec, audio, and non-empty output.
6. Only clips that pass QA are returned as downloads.
7. Per-clip failures are recorded without automatically killing successful clips.

## Security

- `.env` is ignored by Git.
- Do not put API keys in source code, issues, screenshots, or commits.
- For a safer Codespaces setup, use Codespaces Secrets/environment variables instead of committing credentials.

## Project structure

```text
AI-Clipping-Automation/
├── app.py
├── requirements.txt
├── .env.example
├── setup.sh
├── start.sh
├── .devcontainer/devcontainer.json
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

## MVP limitation

This is a Codespaces test MVP, not a production queue. FastAPI background tasks stop if the app/Codespace stops. Large videos and repeated processing consume Codespaces compute and Groq API usage. GitHub Codespaces included usage is quota-based, not unlimited.

## Next phases

- smarter speaker-aware 9:16 reframing
- word-level animated captions
- viral hook/title generation
- campaign-specific templates and compliance rules
- batch processing
- duplicate detection
- render/submission queues
- Whop campaign workflow and analytics
