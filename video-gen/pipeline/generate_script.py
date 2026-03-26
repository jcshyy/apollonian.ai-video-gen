import random
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from templates.meditation_templates import TEMPLATES

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


def generate_script(category: str, topic: str, exercise: str) -> str:
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

Follow this structure exactly:
{structure_text}

Tone:
{template["tone"]}

Style notes:
{style_notes_text}

Target duration:
{template["duration"]}

Reference transcript title:
{reference_title}

Reference transcript:
{reference_transcript}

Requirements:
- Write in a calm, human, supportive voice
- Keep the pacing slow and gentle
- Make the output fit the chosen exercise type
- Use the reference transcript as inspiration for pacing, structure, and style
- Do not copy the reference transcript word-for-word
- Return your response in this exact format:

Title: <short, engaging title for the audio>

Script:
<full script here>

"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    text = response.text.strip()

    # split title + script
    if "Script:" in text:
        title_part, script_part = text.split("Script:", 1)
        title = title_part.replace("Title:", "").strip()
        script = script_part.strip()
    else:
        # fallback if model messes up
        title = "Untitled Audio"
        script = text

    return title, script
