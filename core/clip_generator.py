import subprocess

def render_clip(src, start, end, ass, out):
    subtitle_file = str(ass).replace('\\', '/').replace("'", "\\'")
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,subtitles='" + subtitle_file + "'"
    cmd = ['ffmpeg', '-y', '-ss', str(start), '-to', str(end), '-i', src, '-vf', vf, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(out)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError('FFmpeg failed: ' + p.stderr[-1500:])
