import json
import os
import config

def align(transcript_segments, ocr_results):
    print("Aligning transcript with slide frames...")

    aligned = []
    current_block = {
        "block_id": 0,
        "start_time": 0,
        "end_time": 0,
        "frame_file": "",
        "ocr_text": "",
        "transcript": ""
    }
    block_id = 0

    for seg in transcript_segments:
        seg_start = seg["start"]
        seg_end   = seg["end"]
        seg_text  = seg["text"]

        # Find the closest frame to this transcript segment
        best_frame = None
        best_diff  = float("inf")

        for frame in ocr_results:
            diff = abs(frame["timestamp"] - seg_start)
            if diff < best_diff:
                best_diff  = diff
                best_frame = frame

        # If same frame as previous block, just add text
        if best_frame and aligned and aligned[-1]["frame_file"] == best_frame["frame_file"]:
            aligned[-1]["transcript"] += " " + seg_text
            aligned[-1]["end_time"]    = seg_end
        else:
            # New block
            block = {
                "block_id":      block_id,
                "start_time":    seg_start,
                "end_time":      seg_end,
                "frame_file":    best_frame["frame_file"]     if best_frame else "",
                "ocr_text":      best_frame["ocr_text"]       if best_frame else "",
                "visual_caption": best_frame.get("visual_caption", "") if best_frame else "",
                "transcript":    seg_text
            }
            aligned.append(block)
            block_id += 1

    # Save
    output_path = os.path.join(config.PROCESSED_DIR, "aligned.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(aligned, f, indent=2, ensure_ascii=False)

    print(f"Alignment done! {len(aligned)} blocks created.")
    print(f"Saved to: {output_path}")
    return aligned

if __name__ == "__main__":
    # Load transcript
    transcript_path = os.path.join(config.PROCESSED_DIR, "transcript.json")
    ocr_path        = os.path.join(config.PROCESSED_DIR, "ocr_results.json")

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript_segments = json.load(f)

    with open(ocr_path, "r", encoding="utf-8") as f:
        ocr_results = json.load(f)

    aligned = align(transcript_segments, ocr_results)

    print("\nSample aligned blocks (first 3):")
    for block in aligned[:3]:
        print(f"\n--- Block {block['block_id']} ---")
        print(f"  Time     : {block['start_time']}s → {block['end_time']}s")
        print(f"  Frame    : {block['frame_file']}")
        print(f"  Slide    : {block['ocr_text'][:60]}...")
        print(f"  Speech   : {block['transcript'][:80]}...")