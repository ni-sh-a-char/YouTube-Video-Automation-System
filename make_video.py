import os
import time
import json
import argparse
from ai.gen_subs import gen_subs
from ai.gen_image import gen_image
from ai.gen_voice import gen_voice
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

def gen_video(prompts, args):

    os.makedirs("images", exist_ok=True)
    os.makedirs("audio", exist_ok=True)
    os.makedirs("video", exist_ok=True)
    
    clips = []
    
    for key, value in prompts.items():
        scene_num = key.split('-')[1]
        image_path = f"images/image_{scene_num}.png"
        audio_path = f"audio/voice_{scene_num}.wav"

        if not os.path.exists(image_path):
            print("Generating image...")
            if args.video_format == "video":
                gen_image(value.get("image-prompt"), image_path)
            elif args.video_format == "reel":
                gen_image(value.get("image-prompt"), image_path, 1280, 720)
        else:
            print(f"Image already exists, skipping generation.")
        
        if not os.path.exists(audio_path):
            print("Generating audio...")
            if args.audio_language == "english":
                gen_voice(value.get("narration"), audio_path)
            elif args.audio_language == "hindi":
                gen_voice(value.get("narration"), audio_path, 'h', 'hm_omega')
        else:
            print(f"Audio already exists, skipping generation.")
        
        audio_clip = AudioFileClip(audio_path)
        image_clip = ImageClip(image_path, duration=audio_clip.duration)
        image_clip = image_clip.with_audio(audio_clip)
        clips.append(image_clip)
    
    final_clip = concatenate_videoclips(clips)
    
    final_clip.write_videofile("video/final_video.mp4", fps=24, codec="libx264", audio_codec="aac")
    print(f"Video successfully created at video/final_video.mp4")

    if args.subtitles.lower() == "yes":
        gen_subs(output_srt_path='subtitles.srt', output_video_path='video/final_video_with_subs.mp4', video_format=args.video_format)
        print(f"Video successfully created with subtitles at video/final_video_with_subs.mp4")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="generate videos")
    parser.add_argument("--video_format", "-vf", default="video", help="video/reel")
    parser.add_argument("--audio_language", "-al", default="english", help="english/hindi")
    parser.add_argument("--subtitles", "-s", default="yes", help="yes/no")
    args = parser.parse_args()

    with open('script.json', 'r') as file:
        data = json.load(file)
        prompts = data.get("scene", {})

    start_time = time.time()
    gen_video(prompts, args)
    end_time = time.time()
    print(f"Video successfully created in {end_time - start_time} seconds.")