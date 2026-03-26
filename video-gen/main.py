from pipeline.generate_script import generate_script
from pipeline.generate_audio import generate_audio
from pipeline.generate_visuals import generate_visuals
from pipeline.assemble_video import assemble_video


EXERCISE_OPTIONS = {
    "1": "breathing",
    "2": "reframing_negative_thoughts",
    "3": "thought_diffusion",
    "4": "self_compassion",
}


def run_pipeline():
    category = "anxiety"
    topic = input("Enter the topic: ").strip()

    print("\nChoose an exercise category:")
    print("1. Breathing")
    print("2. Challenge Negative Thoughts")
    print("3. Distance Yourself From Anxious Thoughts")
    print("4. Self-Compassion")

    choice = input("Enter 1, 2, 3, or 4: ").strip()
    exercise = EXERCISE_OPTIONS.get(choice)

    if not exercise:
        print("Invalid choice. Defaulting to breathing.\n")
        exercise = "breathing"

    print("[1] Generating script...")
    title, script = generate_script(category, topic, exercise)

    print(f"Title: {title}")

    print("\nGenerated Script:\n")
    print(script)


    print("\n[2] Generating audio...")
    audio_path = generate_audio(script, "data/audio/anxiety_test.wav")
    print(f"Audio saved at: {audio_path}")

    print("\n[3] Generating visuals...")
    visual_path = generate_visuals(script)
    print(f"Visual saved at: {visual_path}")

    print("\n[4] Assembling video...")
    video_path = assemble_video(audio_path, visual_path)
    print(f"\nDone. Final video saved at: {video_path}")


if __name__ == "__main__":
    run_pipeline()