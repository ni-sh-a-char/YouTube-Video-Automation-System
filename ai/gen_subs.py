import os
import pysrt
import whisper
import subprocess
import imageio_ffmpeg
import shutil

def gen_subs(output_srt_path, input_video_path, output_video_path, video_format, model_size="tiny"):
    """
    Generate subtitles using Whisper and burn them into video.
    Uses imageio-ffmpeg to ensure ffmpeg is available.
    """
    # Ensure ffmpeg is available
    import platform
    import stat
    
    is_windows = platform.system() == "Windows"
    ffmpeg_filename = "ffmpeg.exe" if is_windows else "ffmpeg"
    
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Whisper expects 'ffmpeg' to be in PATH, but imageio might have a weird name
        # So we copy it to a local bin folder as 'ffmpeg' (or 'ffmpeg.exe')
        bin_dir = os.path.join(os.getcwd(), 'bin')
        os.makedirs(bin_dir, exist_ok=True)
        
        dest_ffmpeg = os.path.join(bin_dir, ffmpeg_filename)
        
        # Always copy if missing or update if needed (simple check: if not exists)
        if not os.path.exists(dest_ffmpeg):
            print(f"DEBUG: Copying {ffmpeg_exe} to {dest_ffmpeg}...")
            shutil.copy(ffmpeg_exe, dest_ffmpeg)
            
            # Make executable on Linux/Mac
            if not is_windows:
                st = os.stat(dest_ffmpeg)
                os.chmod(dest_ffmpeg, st.st_mode | stat.S_IEXEC)
                print(f"DEBUG: Made {dest_ffmpeg} executable")
            
        # Prepend bin to PATH
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
        
        # Update ffmpeg_exe to verify we use the new one
        ffmpeg_exe = dest_ffmpeg
        
        print(f"DEBUG: ffmpeg setup complete. Path: {ffmpeg_exe}")
        print(f"DEBUG: shutil.which('ffmpeg') found: {shutil.which('ffmpeg')}")
        
    except Exception as e:
        print(f"Warning: Could not set ffmpeg path from imageio: {e}")

    if not os.path.exists(output_srt_path):
        # === STEP 1: Extract Audio ===
        audio_path = "audio/extracted_audio.wav"
        print(f"[*] Extracting audio using {ffmpeg_exe}...")
        subprocess.run([
            ffmpeg_exe, '-y',
            '-i', input_video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            audio_path
        ], check=True)

        # === STEP 2: Transcribe using Whisper (with timestamps) ===
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path)

        # === STEP 3: Match provided text with Whisper segments ===
        subs = pysrt.SubRipFile()

        for i, segment in enumerate(result['segments']):
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()

            sub = pysrt.SubRipItem(
                index=i + 1,
                start=pysrt.SubRipTime(seconds=start),
                end=pysrt.SubRipTime(seconds=end),
                text=text
            )
            subs.append(sub)

        # === STEP 4: Save .srt file ===
        subs.save(output_srt_path, encoding='utf-8')

    # === STEP 5: Embed subtitles into video using ffmpeg ===

    if video_format=="video":
        subprocess.run([
            ffmpeg_exe,
            '-i', input_video_path,
            '-vf', f"subtitles={output_srt_path}",
            '-c:a', 'copy',
            output_video_path
        ])
    elif video_format=="reel":
        subprocess.run([
            ffmpeg_exe,
            '-i', input_video_path,
            '-vf', f"subtitles='{output_srt_path}':force_style='Fontsize=20,Alignment=10,MarginV=50'",
            '-c:a', 'copy',
            output_video_path
        ])