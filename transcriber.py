import whisper
import librosa
import json
import os
import config

def transcribe_audio(audio_path):
    print(f"Loading Whisper model: {config.WHISPER_MODEL}")
    model = whisper.load_model(config.WHISPER_MODEL)

    print(f"Loading audio file...")
    # Load audio using librosa (bypasses ffmpeg completely)
    audio, sr = librosa.load(audio_path, sr=16000, mono=True)

    print("Transcribing... please wait (3-5 mins on CPU)")
    result = model.transcribe(audio)

    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": round(seg["start"], 2),
            "end":   round(seg["end"], 2),
            "text":  seg["text"].strip()
        })

    output_path = os.path.join(config.PROCESSED_DIR, "transcript.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    print(f"Transcription done! {len(segments)} segments saved.")
    print(f"Saved to: {output_path}")
    return segments

if __name__ == "__main__":
    audio_path = os.path.join(config.AUDIO_DIR, "audio.wav")
    if os.path.exists(audio_path):
        segments = transcribe_audio(audio_path)
        print("\nFirst 3 segments:")
        for s in segments[:3]:
            print(f"  [{s['start']}s → {s['end']}s] {s['text']}")
    else:
        print("audio.wav not found! Run extractor.py first.")