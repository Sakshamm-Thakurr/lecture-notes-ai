import pytesseract
import json
import os
from PIL import Image
import config

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

# ── BLIP-2 Vision Setup ──────────────────────────────────────────────
print("Loading BLIP vision model... (first time = slow, after that fast)")
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model     = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base",
    torch_dtype=torch.float32
)
blip_model.eval()
print("BLIP vision model loaded!")

def caption_image(image_path):
    try:
        image  = Image.open(image_path).convert("RGB")
        inputs = blip_processor(image, return_tensors="pt")
        with torch.no_grad():
            out = blip_model.generate(**inputs, max_new_tokens=60)
        caption = blip_processor.decode(out[0], skip_special_tokens=True)
        return caption.strip()
    except Exception as e:
        return ""

def process_frames(frames_list):
    print(f"Processing {len(frames_list)} frames with OCR + Vision...")
    results = []

    for i, frame_info in enumerate(frames_list):
        frame_path = os.path.join(config.FRAMES_DIR, frame_info["frame_file"])

        if not os.path.exists(frame_path):
            continue

        # OCR — reads slide text
        img      = Image.open(frame_path)
        ocr_text = pytesseract.image_to_string(img).strip()
        lines    = [l.strip() for l in ocr_text.split("\n") if l.strip()]
        clean_ocr = " | ".join(lines) if lines else ""

        # BLIP — describes visual content (diagrams, graphs, images)
        visual_caption = caption_image(frame_path)

        results.append({
            "frame_file":     frame_info["frame_file"],
            "timestamp":      frame_info["timestamp"],
            "ocr_text":       clean_ocr,
            "visual_caption": visual_caption
        })

        print(f"  [{i+1}/{len(frames_list)}] OCR: {clean_ocr[:40]}... | Vision: {visual_caption[:40]}...")

    # Save
    output_path = os.path.join(config.PROCESSED_DIR, "ocr_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {len(results)} frames processed with OCR + Vision.")
    print(f"Saved to: {output_path}")
    return results

if __name__ == "__main__":
    frames_list = []
    frame_files = sorted([f for f in os.listdir(config.FRAMES_DIR) if f.endswith(".jpg")])

    for i, fname in enumerate(frame_files):
        frames_list.append({
            "frame_file": fname,
            "timestamp":  float(i * config.FRAME_INTERVAL)
        })

    print(f"Found {len(frames_list)} frames")
    results = process_frames(frames_list)

    print("\nSample results (first 3):")
    for r in results[:3]:
        print(f"\n  Frame    : {r['frame_file']}")
        print(f"  OCR text : {r['ocr_text'][:60]}")
        print(f"  Vision   : {r['visual_caption']}")