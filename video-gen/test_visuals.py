from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from pipeline.generate_visuals import generate_visuals

audio_path = "data/audio/anxiety_test.wav"
visual_info = generate_visuals(
    audio_path= audio_path,
    min_clip_duration=30
)

print("Total duration:", visual_info["total_duration"])

for clip in visual_info["clips"]:
    print("Clip:", clip["video_path"])
    print("Attribution:", clip["attribution"])