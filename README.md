# 🎓 Lecture Notes AI

> Automatically convert lecture videos into structured study notes — powered by AI.

Lecture Notes AI is a college project that takes lecture videos (MP4 files or YouTube links) and transforms them into clean, readable PDF study notes using speech transcription, slide extraction, and AI-based note generation.

---

## ✨ Features

- 🎬 **Video Input Support** — Works with local MP4 files and YouTube links
- 🔊 **Audio Transcription** — Extracts and transcribes spoken content from lectures
- 🖼️ **Slide Extraction** — Captures key frames from lecture videos
- 🧠 **AI Note Generation** — Aligns transcription with slides to generate structured notes
- 📄 **PDF Export** — Outputs final study notes as a downloadable PDF

---

## 🗂️ Project Structure

```
lecture-notes-ai/
│
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── transcriber.py          # Audio transcription module
├── extractor.py            # Frame & audio extraction from video
├── slide_processor.py      # Processes extracted slide frames (OCR)
├── aligner.py              # Aligns transcript with slide content
├── note_generator.py       # Generates structured notes using AI
├── pdf_builder.py          # Builds and exports the final PDF
│
├── input/                  # Place your video files here
├── extracted/              # Auto-generated frames and audio
├── processed/              # Intermediate JSON outputs
└── output/                 # Final PDF study notes
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sakshamm-Thakurr/lecture-notes-ai.git
   cd lecture-notes-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Usage

**Option 1 — Local video file:**
```bash
python app.py --input input/your_lecture.mp4
```

**Option 2 — YouTube link:**
```bash
python app.py --url "https://www.youtube.com/watch?v=your_video_id"
```

The output PDF will be saved in the `output/` folder.

---

## 🛠️ Tech Stack

| Purpose | Tool |
|---|---|
| Transcription | Whisper (OpenAI) |
| OCR / Slide Processing | Tesseract / OpenCV |
| Note Generation | AI / NLP |
| PDF Generation | Python PDF libraries |
| YouTube Download | yt-dlp / pytube |

---

## 📸 How It Works

```
Video / YouTube URL
       ↓
  Extract Audio & Frames
       ↓
  Transcribe Audio (Whisper)
       ↓
  OCR on Slide Frames
       ↓
  Align Transcript + Slides
       ↓
  Generate Study Notes (AI)
       ↓
  Export as PDF 📄
```

---

## 👨‍💻 Author

**Saksham Thakur**
College Project — Built with ❤️ to make studying easier

---

## 📜 License

This project is for educational purposes.
