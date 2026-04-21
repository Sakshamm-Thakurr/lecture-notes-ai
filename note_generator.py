import json
import os
import urllib.request
import config

def ask_ollama(prompt):
    data = json.dumps({
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["response"].strip()

def generate_notes(aligned_blocks):
    print(f"Generating notes for {len(aligned_blocks)} blocks using Ollama...")
    print("This may take 5-10 minutes. Please wait...\n")

    notes = []

    for i, block in enumerate(aligned_blocks):
        transcript = block["transcript"].strip()
        ocr_text   = block["ocr_text"].strip()

        # Skip blocks with very little content
        if len(transcript) < 20:
            continue
          
        visual = block.get("visual_caption", "")  
        prompt = f"""You are a helpful study note assistant.

A professor said this:
\"{transcript}\"

Slide text visible on screen:
\"{ocr_text if ocr_text else 'No slide text'}\"

Visual content on slide (diagram/image description):
\"{visual if visual else 'No visual content'}\"

Generate study notes in this exact format:
HEADING: (a short 5-word heading)
BULLETS:
- (key point 1)
- (key point 2)
- (key point 3)
SUMMARY: (1-2 sentence summary)
QUESTION: (one practice question)

Be concise and clear."""

        print(f"  Generating block {i+1}/{len(aligned_blocks)}...", end=" ")
        try:
            response = ask_ollama(prompt)
            notes.append({
                "block_id":   block["block_id"],
                "start_time": block["start_time"],
                "end_time":   block["end_time"],
                "frame_file": block["frame_file"],
                "notes":      response
            })
            print("done")
        except Exception as e:
            print(f"error: {e}")
            continue

    # Save
    output_path = os.path.join(config.PROCESSED_DIR, "notes.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

    print(f"\nNotes generated! {len(notes)} blocks saved.")
    print(f"Saved to: {output_path}")
    return notes

if __name__ == "__main__":
    aligned_path = os.path.join(config.PROCESSED_DIR, "aligned.json")

    with open(aligned_path, "r", encoding="utf-8") as f:
        aligned_blocks = json.load(f)

    notes = generate_notes(aligned_blocks)

    print("\nSample note (first block):")
    if notes:
        print(notes[0]["notes"])