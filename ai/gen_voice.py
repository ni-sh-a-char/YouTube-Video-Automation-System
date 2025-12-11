from gtts import gTTS
import os

def gen_voice(prompt, audio_path, lang_code='en', voice=None):
    """
    Generate voice using Google Text-to-Speech (gTTS).
    Lightweight, no GPU required.
    """
    try:
        print(f"[*] Generating voice via gTTS: {prompt[:30]}...")
        tts = gTTS(text=prompt, lang=lang_code, slow=False)
        tts.save(audio_path)
        print(f"[OK] Audio saved to {audio_path}")
    except Exception as e:
        print(f"[!] Error generating voice: {e}")