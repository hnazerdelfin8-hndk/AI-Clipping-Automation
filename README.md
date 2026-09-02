# AI Clipping Automation — Phone-Friendly MVP

MP4 → Groq Whisper → AI moment finder → FFmpeg → 9:16 → captions → QA → downloadable clips.

## Run in GitHub Codespaces

1. Open this repository in a Codespace.
2. Install FFmpeg if needed:
   `sudo apt-get update && sudo apt-get install -y ffmpeg`
3. Install Python packages:
   `pip install -r requirements.txt`
4. Create `.env` from `.env.example` and add your Groq API key. Never commit `.env`.
5. Load it:
   `set -a; source .env; set +a`
6. Start the app:
   `uvicorn app:app --host 0.0.0.0 --port 8000`
7. Open forwarded port 8000 and upload an MP4.

## MVP scope

- Groq Whisper transcription with segment timestamps
- LLM selection of up to 5 short-form moments
- FFmpeg 1080x1920 rendering
- Burned-in ASS captions
- Basic output QA
- Browser upload and download UI

This is a test MVP, not a production service. Long videos and repeated processing consume compute and API usage.
