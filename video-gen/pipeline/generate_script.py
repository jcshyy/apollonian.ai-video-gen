import random
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from templates.meditation_templates import TEMPLATES
import os
from dotenv import load_dotenv

load_dotenv()

import time

def generate_with_retry(client, model, contents, config=None, retries=4):
    delays = [1, 2, 4, 8]
    last_error = None

    for i in range(retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            last_error = e
            msg = str(e)

            if "503" in msg or "UNAVAILABLE" in msg:
                if i < len(delays):
                    print(f"Gemini overloaded, retrying in {delays[i]}s...")
                    time.sleep(delays[i])
                    continue

            raise

    raise last_error

REFERENCE_TRANSCRIPTS = {
    "breathing": [
        {
            "title": "Calm Your Heart With Deeper Breaths",
            "path": "data/transcripts/calm_breathing.txt",
        },
        {
            "title": "5 Minute Emergency Calm",
            "path": "data/transcripts/5minEmergencyCalm.txt",
        },
    ],
    "reframing_negative_thoughts": [
        {
            "title": "Challenge Your Negative Thoughts",
            "path": "data/transcripts/challenge_negative_thoughts.txt",
        },
    ],
    "thought_diffusion": [
        {
            "title": "Distance Yourself From Anxious Thoughts",
            "path": "data/transcripts/distance_anxious_thoughts.txt",
        },
    ],
    "self_compassion": [
        {
            "title": "Replace Self Criticism with Self-Compassion",
            "path": "data/transcripts/self_compassion.txt",
        },
    ],
}


def load_reference_transcript(exercise: str) -> tuple[str, str]:
    if exercise not in REFERENCE_TRANSCRIPTS:
        raise ValueError(f"No reference transcript found for exercise '{exercise}'")

    options = REFERENCE_TRANSCRIPTS[exercise]
    item = random.choice(options)

    with open(item["path"], "r", encoding="utf-8") as f:
        transcript = f.read().strip()

    return item["title"], transcript


def generate_script(category: str, topic: str, exercise: str) -> tuple[str, str]:
    if category not in TEMPLATES:
        raise ValueError(f"Template '{category}' not found.")

    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY.")

    template = TEMPLATES[category]
    client = genai.Client(api_key=GEMINI_API_KEY)

    reference_title, reference_transcript = load_reference_transcript(exercise)

    structure_text = "\n".join(f"- {section}" for section in template["structure"])
    style_notes_text = "\n".join(f"- {note}" for note in template["style_notes"])

    prompt = f"""
You are writing a calm, supportive mental health guided audio script.

Category: {category}
Topic: {topic}
Exercise type: {exercise}

IMPORTANT:
- The script MUST center around the topic: "{topic}"
- Every section should clearly support this topic
- Do NOT drift into general anxiety or generic meditation unless it directly supports the topic

Reference transcript title:
{reference_title}

Reference transcript:
{reference_transcript}

Instructions for using the reference transcript:
- Use it as inspiration for structure, pacing, and emotional flow
- Do NOT copy phrases or sentences directly
- The output should feel like a rewritten and improved version, not a duplicate
- Follow the progression of ideas from the transcript when possible
- The script should stay original while clearly reflecting the transcript's overall approach

Use this structure as a guideline, but adapt it to best fit the topic and reference transcript:
{structure_text}

Tone:
{template["tone"]}

Style notes:
{style_notes_text}

Target duration:
{template["duration"]}

Requirements:
- Write in a calm, human, supportive voice
- Keep the pacing slow and gentle
- Make the output fit the chosen exercise type
- Avoid generic meditation openings (e.g. "find a comfortable place to sit or lie down") unless it clearly fits the topic
- The opening should feel specific to the topic, not generic
- Include pauses like "pause" or "pause longer" for pacing
- Keep transitions smooth and natural
- Do NOT repeat common meditation phrases unless they are necessary for the topic

Goal:
The final script should feel like it belongs in a high-quality meditation app
and clearly reflect the topic "{topic}" throughout.

Return your response in this exact format:

Title: <short, engaging title for the audio>

Script:
<full script here>
"""

    response = generate_with_retry(
        client=client,
        model=GEMINI_MODEL,
        contents=prompt,
    )

    text = response.text.strip()

    # Split title + script safely
    if "Script:" in text:
        title_part, script_part = text.split("Script:", 1)
        title = title_part.replace("Title:", "").strip()
        script = script_part.strip()
    else:
        # fallback if model messes up
        title = "Untitled Audio"
        script = text

    return title, script