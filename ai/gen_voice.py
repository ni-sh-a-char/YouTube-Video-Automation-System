from kokoro import KPipeline
import soundfile as sf
import torch

def gen_voice(prompt, audio_path, lang_code='b', voice='bm_lewis'):
    pipeline = KPipeline(lang_code)
    generator = pipeline(prompt, voice=voice)
    for i, (gs, ps, audio) in enumerate(generator):
        print(i, gs, ps)
        sf.write(audio_path, audio, 24000)