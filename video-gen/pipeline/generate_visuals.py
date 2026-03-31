from pathlib import Path
import os
import requests
from dotenv import load_dotenv
from moviepy import AudioFileClip

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_VIDEO_URL = "https://api.pexels.com/v1/videos/search"

DOWNLOAD_DIR = Path("data/visuals")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_audio_duration(audio_path: str) -> int:
    audio = AudioFileClip(audio_path)
    duration = int(audio.duration)
    audio.close()
    return duration


def search_pexels_videos(query: str = "peaceful nature slow", per_page: int = 15, page: int = 1):
    if not PEXELS_API_KEY:
        raise ValueError("Missing PEXELS_API_KEY.")

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "per_page": per_page,
        "page": page,
        "orientation": "landscape",
        "size": "medium",
    }

    response = requests.get(PEXELS_VIDEO_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def pick_best_file(video: dict):
    files = video.get("video_files", [])
    if not files:
        return None

    mp4_files = [f for f in files if f.get("file_type") == "video/mp4"]
    if not mp4_files:
        return None

    return sorted(mp4_files, key=lambda x: x.get("width", 0), reverse=True)[0]


def download_video(video_url: str, filename: str):
    output_path = DOWNLOAD_DIR / filename

    with requests.get(video_url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    return str(output_path)


def generate_visuals(audio_path: str, min_clip_duration: int = 30):
    target_total_duration = get_audio_duration(audio_path)
    print("Target duration from audio:", target_total_duration)

    results = []
    seen_video_ids = set()
    total_duration = 0
    clip_index = 1

    for page in range(1, 6):
        data = search_pexels_videos(query="nature", per_page=15, page=page)
        videos = data.get("videos", [])

        for video in videos:
            video_id = video.get("id")
            duration = video.get("duration", 0)

            if video_id in seen_video_ids:
                continue
            if duration < min_clip_duration:
                continue

            best_file = pick_best_file(video)
            if not best_file:
                continue

            filename = f"nature_clip_{clip_index}.mp4"
            path = download_video(best_file["link"], filename)

            results.append({
                "video_path": path,
                "duration": duration,
                "attribution": f"Video by {video.get('user', {}).get('name', 'Unknown')} on Pexels",
                "pexels_page": video.get("url", ""),
            })

            seen_video_ids.add(video_id)
            total_duration += duration
            clip_index += 1

            print(f"Downloaded {filename} ({duration}s). Total so far: {total_duration}s")

            if total_duration >= target_total_duration:
                return {
                    "clips": results,
                    "total_duration": total_duration,
                }

    if not results:
        raise ValueError("No suitable nature videos found.")

    return {
        "clips": results,
        "total_duration": total_duration,
    }