from pathlib import Path
import wave
import os
import asyncio

import edge_tts
from google import genai
from google.genai import types


VOICE_NAME = "Kore"
EDGE_VOICE = "en-US-AriaNeural"
USE_GEMINI = True



def _save_pcm_as_wav(pcm_data: bytes, output_path: str, sample_rate: int = 24000) -> None:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(output_file), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)


def generate_audio_gemini(script: str, output_path: str = "data/audio/output.wav") -> str:
    print("word count:", len(script.split()))

    if not script.strip():
        raise ValueError("Script is empty.")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment.")

    Path("data/audio").mkdir(parents=True, exist_ok=True)

    client = genai.Client(api_key=api_key)

    prompt = f"""
Read this exactly as written in a calm, warm, grounding meditation voice. And add short and long 
pauses when needed.


{script}
""".strip()

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=VOICE_NAME
                    )
                )
            ),
        ),
    )

    audio_chunks = []

    for candidate in response.candidates:
        if not candidate.content or not candidate.content.parts:
            continue

        for part in candidate.content.parts:
            if getattr(part, "inline_data", None) and part.inline_data and part.inline_data.data:
                audio_chunks.append(part.inline_data.data)

    if not audio_chunks:
        raise ValueError("No audio returned from Gemini TTS.")


    print(f"Script length: {len(script)} characters")
    print(f"Script length: {len(script)} characters")
    
    audio_bytes = b"".join(audio_chunks)

    _save_pcm_as_wav(audio_bytes, output_path)
    print(f"Gemini audio saved at: {output_path}")
    return output_path


async def _generate_audio_edge_async(script: str, output_path: str) -> str:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    communicate = edge_tts.Communicate(script, EDGE_VOICE)
    await communicate.save(str(output_file))

    print(f"Edge audio saved at: {output_path}")
    return output_path


def generate_audio_edge(script: str, output_path: str = "data/audio/output.mp3") -> str:
    if not script.strip():
        raise ValueError("Script is empty.")

    return asyncio.run(_generate_audio_edge_async(script, output_path))

def generate_audio(script: str, output_path: str = "data/audio/output.wav") -> str:
    if USE_GEMINI:
        try:
            return generate_audio_gemini(script, output_path)
        except Exception as e:
            print(f"Gemini failed, falling back to Edge TTS: {e}")

            fallback_path = output_path
            if fallback_path.endswith(".wav"):
                fallback_path = fallback_path[:-4] + ".mp3"

            return generate_audio_edge(script, fallback_path)

    fallback_path = output_path
    if fallback_path.endswith(".wav"):
        fallback_path = fallback_path[:-4] + ".mp3"

    return generate_audio_edge(script, fallback_path)