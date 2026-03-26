from pathlib import Path

def generate_visuals(script: str, output_path: str = "assets/calm_video.mp4") -> str:
    video_path = Path(output_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Background video not found: {video_path}")

    return str(video_path)