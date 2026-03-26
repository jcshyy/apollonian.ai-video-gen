from pathlib import Path
from moviepy import AudioFileClip, VideoFileClip

def assemble_video(audio_path: str, visual_path: str, output_path: str = "data/videos/final_video.mp4") -> str:
    Path("data/videos").mkdir(parents=True, exist_ok=True)

    audio_clip = AudioFileClip(audio_path)
    video_clip = VideoFileClip(visual_path)

    #  REMOVE background video audio
    video_clip = video_clip.without_audio()

    # match duration + attach narration
    final_video = video_clip.with_duration(audio_clip.duration).with_audio(audio_clip)

    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    audio_clip.close()
    video_clip.close()
    final_video.close()

    return output_path