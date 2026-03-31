from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips


def assemble_video(audio_path: str, visual_data: dict, output_path: str = "data/videos/final_video.mp4"):
    clips_data = visual_data.get("clips", [])
    if not clips_data:
        raise ValueError("visual_data must include at least one clip in 'clips'.")

    Path("data/videos").mkdir(parents=True, exist_ok=True)

    audio = AudioFileClip(audio_path)
    target_duration = audio.duration
    video_clips = []
    combined_video = None
    final_video = None
    try:
        for clip_data in clips_data:
            video_path = clip_data["video_path"]
            video_clips.append(VideoFileClip(video_path))

        combined_video = concatenate_videoclips(video_clips, method="compose")
        final_video = combined_video.subclipped(0, min(combined_video.duration, target_duration))

        # remove original clip audio if it has any, then add narration audio
        final_video = final_video.without_audio()
        final_video = final_video.with_audio(audio)

        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=24
        )
    finally:
        if final_video is not None:
            final_video.close()
        if combined_video is not None:
            combined_video.close()
        audio.close()
        for clip in video_clips:
            clip.close()

    return output_path
