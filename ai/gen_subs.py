import os
import pysrt
import whisper
import subprocess
from moviepy import VideoFileClip

def gen_subs(output_srt_path, output_video_path, video_format):

    input_video_path = 'video/final_video.mp4'

    if not os.path.exists(output_srt_path):
        # === INPUTS ===
        model_size = "medium"  # Choose model size: tiny, base, small, medium, large, large-v2

        # === STEP 1: Extract Audio ===
        clip = VideoFileClip(input_video_path)
        audio_path = "audio/extracted_audio.wav"
        clip.audio.write_audiofile(audio_path)

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
            'ffmpeg',
            '-i', input_video_path,
            '-vf', f"subtitles={output_srt_path}",
            '-c:a', 'copy',
            output_video_path
        ])
    elif video_format=="reel":
        subprocess.run([
            'ffmpeg',
            '-i', input_video_path,
            '-vf', f"subtitles='{output_srt_path}':force_style='Fontsize=20,Alignment=10,MarginV=50'",
            '-c:a', 'copy',
            output_video_path
        ])