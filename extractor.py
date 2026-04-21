import cv2
import os
import config
from moviepy import VideoFileClip

def extract_audio(video_path):
    print(f"Extracting audio from: {video_path}")
    audio_path = os.path.join(config.AUDIO_DIR, "audio.wav")
    
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, fps=16000, nbytes=2, ffmpeg_params=["-ac", "1"])
    video.close()
    
    print(f"Audio saved to: {audio_path}")
    return audio_path

def extract_frames(video_path):
    print(f"Extracting frames from: {video_path}")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(fps * config.FRAME_INTERVAL)
    frame_count = 0
    saved_count = 0
    saved_frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % interval == 0:
            filename = f"frame_{saved_count:04d}.jpg"
            path = os.path.join(config.FRAMES_DIR, filename)
            cv2.imwrite(path, frame)
            timestamp = frame_count / fps
            saved_frames.append({
                "frame_file": filename,
                "timestamp": round(timestamp, 2)
            })
            saved_count += 1
        frame_count += 1

    cap.release()
    print(f"Extracted {saved_count} frames")
    return saved_frames

if __name__ == "__main__":
    test_video = input("Enter full path of your lecture video: ").strip()
    if os.path.exists(test_video):
        audio = extract_audio(test_video)
        frames = extract_frames(test_video)
        print(f"\nDone!")
        print(f"Audio saved: {audio}")
        print(f"Total frames extracted: {len(frames)}")
        print(f"First 3 frames: {frames[:3]}")
    else:
        print("Video file not found. Check the path.")