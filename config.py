import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
AUDIO_DIR = os.path.join(BASE_DIR, "extracted", "audio")
FRAMES_DIR = os.path.join(BASE_DIR, "extracted", "frames")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

# Tesseract path
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Whisper model size: "tiny", "base", "small"
# Use "base" for good accuracy on normal laptop
WHISPER_MODEL = "base"

# How often to extract a frame (every N seconds)
FRAME_INTERVAL = 8

# Ollama model name
OLLAMA_MODEL = "llama3.2"

print("Config loaded successfully!")