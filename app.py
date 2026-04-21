import streamlit as st
import os
import json
import subprocess
import config
from extractor import extract_audio, extract_frames
from transcriber import transcribe_audio
from slide_processor import process_frames
from aligner import align
from note_generator import generate_notes, ask_ollama
from pdf_builder import build_pdf

st.set_page_config(
    page_title="Lecture Notes AI",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Lecture Video → Smart Study Notes")
st.markdown("Upload a lecture video or paste a URL to get AI-generated study notes + chat with your lecture!")
st.divider()

# ── Helper: find relevant notes for a question ──────────────────────
def find_relevant_blocks(question, notes, top_k=3):
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        texts        = [n["notes"] for n in notes]
        texts_with_q = texts + [question]

        vectorizer   = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(texts_with_q)

        question_vec = tfidf_matrix[-1]
        notes_vecs   = tfidf_matrix[:-1]

        similarities = cosine_similarity(question_vec, notes_vecs)[0]
        top_indices  = np.argsort(similarities)[-top_k:][::-1]

        return [notes[i] for i in top_indices]
    except:
        return notes[:3]

# ── Download video from URL using yt-dlp ────────────────────────────
def download_from_url(url, status_placeholder):
    try:
        video_path = os.path.join(config.INPUT_DIR, "downloaded_video.mp4")

        # Remove old file if exists
        if os.path.exists(video_path):
            os.remove(video_path)

        status_placeholder.info("⏳ Downloading video from URL... please wait")

        command = [
            "python", "-m", "yt_dlp",
            "-f", "best[ext=mp4]/best",
            "-o", video_path,
            "--no-playlist",
            url
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and os.path.exists(video_path):
            size_mb = round(os.path.getsize(video_path) / 1e6, 1)
            status_placeholder.success(f"✅ Video downloaded successfully! ({size_mb} MB)")
            return video_path, "Downloaded Video"
        else:
            error_msg = result.stderr[:300] if result.stderr else "Unknown error"
            status_placeholder.error(f"Download failed: {error_msg}")
            return None, None

    except Exception as e:
        status_placeholder.error(f"Error during download: {e}")
        return None, None

# ── Load existing notes if already processed ────────────────────────
def load_existing_notes():
    notes_path = os.path.join(config.PROCESSED_DIR, "notes.json")
    if os.path.exists(notes_path):
        with open(notes_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# ── Main UI ──────────────────────────────────────────────────────────
existing_notes = load_existing_notes()

if existing_notes:
    st.success(f"✅ Previously processed notes found! ({len(existing_notes)} blocks)")
    use_existing = st.checkbox("Use existing notes (skip processing)", value=True)
else:
    use_existing = False

# ── Input Method Selector ────────────────────────────────────────────
st.subheader("Input Source")
input_method = st.radio(
    "Choose how to provide your lecture:",
    ["Upload Video File", "Paste Video URL"],
    horizontal=True
)

video_url     = None
uploaded_file = None

if input_method == "Upload Video File":
    uploaded_file = st.file_uploader(
        "Upload your lecture video",
        type=["mp4", "avi", "mov", "mkv", "mpeg4"]
    )

else:
    video_url = st.text_input(
        "Paste video URL here",
        placeholder="https://www.youtube.com/watch?v=..."
    )
    st.caption("✅ Supports: YouTube · Vimeo · Dailymotion · 1000+ platforms")
    st.caption("⚠️ LinkedIn Learning requires login — download manually and upload instead")

    if video_url:
        st.info(f"🔗 URL ready: {video_url[:70]}...")

notes = None

# ── Use existing notes ───────────────────────────────────────────────
if use_existing and existing_notes:
    notes = existing_notes

# ── Process button ───────────────────────────────────────────────────
can_process = (uploaded_file is not None or bool(video_url)) and not use_existing

if can_process:
    if st.button("🚀 Generate Study Notes", type="primary", use_container_width=True):

        progress   = st.progress(0)
        status     = st.empty()
        video_path = None

        # ── Handle URL download ──────────────────────────────────────
        if video_url:
            video_path, vid_title = download_from_url(video_url, status)
            if not video_path:
                st.stop()
            progress.progress(10)

        # ── Handle file upload ───────────────────────────────────────
        elif uploaded_file:
            video_path = os.path.join(config.INPUT_DIR, uploaded_file.name)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            status.success(f"✅ File uploaded: {uploaded_file.name}")
            progress.progress(10)

        # ── Run full pipeline ────────────────────────────────────────
        try:
            status.info("Step 1/5 — Extracting audio and frames from video...")
            audio_path = extract_audio(video_path)
            frames     = extract_frames(video_path)
            progress.progress(25)

            status.info("Step 2/5 — Transcribing speech with Whisper AI...")
            segments = transcribe_audio(audio_path)
            progress.progress(45)

            status.info("Step 3/5 — Reading slides with OCR + BLIP Vision AI...")
            ocr_results = process_frames(frames)
            progress.progress(62)

            status.info("Step 4/5 — Aligning speech with slide content...")
            aligned = align(segments, ocr_results)
            progress.progress(75)

            status.info("Step 5/5 — Generating AI study notes with Llama 3.2...")
            notes    = generate_notes(aligned)
            pdf_path = build_pdf(notes)
            progress.progress(100)

            status.success("🎉 All done! Your study notes are ready below!")
            st.session_state.notes = notes

        except Exception as e:
            status.error(f"Something went wrong: {e}")
            st.exception(e)

# ── Tabs: Notes + Chat ───────────────────────────────────────────────
if notes:
    st.divider()
    tab1, tab2 = st.tabs(["📄 Study Notes PDF", "💬 Chat with Lecture"])

    # ── Tab 1: PDF ───────────────────────────────────────────────────
    with tab1:
        pdf_path = os.path.join(config.OUTPUT_DIR, "study_notes.pdf")

        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Study Notes PDF",
                    data=f,
                    file_name="study_notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        st.divider()

        # Stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Note Blocks",    len(notes))
        col2.metric("Topics Covered", len(set(
            n["notes"].split("\n")[0].replace("HEADING:", "").strip()
            for n in notes if n["notes"]
        )))
        col3.metric("Time Covered",   f"{int(notes[-1]['end_time']//60)} min")

        st.divider()

        # Notes preview
        st.subheader("Notes Preview (first 5 blocks)")
        for i, note in enumerate(notes[:5]):
            heading = note["notes"].split("\n")[0][:60] if note["notes"] else f"Block {i+1}"
            with st.expander(f"Block {i+1} — {heading}"):
                st.text(note["notes"])
                frame_path = os.path.join(config.FRAMES_DIR, note.get("frame_file", ""))
                if os.path.exists(frame_path):
                    st.image(frame_path, width=300, caption="Slide at this timestamp")

    # ── Tab 2: Chat ──────────────────────────────────────────────────
    with tab2:
        st.subheader("💬 Ask anything about this lecture")
        st.caption("Answers are grounded only in what was taught in this video")

        # Quick question buttons
        st.markdown("**Quick questions to try:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("What is the main topic?", use_container_width=True):
                st.session_state.quick_q = "What is the main topic of this lecture?"
        with col2:
            if st.button("Summarize the lecture", use_container_width=True):
                st.session_state.quick_q = "Give me a full summary of this lecture"

        col3, col4 = st.columns(2)
        with col3:
            if st.button("Key concepts covered", use_container_width=True):
                st.session_state.quick_q = "What are the key concepts covered in this lecture?"
        with col4:
            if st.button("Important definitions", use_container_width=True):
                st.session_state.quick_q = "List all important definitions from this lecture"

        st.divider()

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display existing chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Handle quick question
        if "quick_q" in st.session_state and st.session_state.quick_q:
            question = st.session_state.quick_q
            st.session_state.quick_q = None

            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)

            relevant = find_relevant_blocks(question, notes)
            context  = "\n\n".join([
                f"[{r['start_time']}s-{r['end_time']}s]: {r['notes']}"
                for r in relevant
            ])
            prompt = f"""You are a helpful study assistant.
Lecture notes context:
{context}

Student question: {question}

Answer clearly based only on the lecture content above.
If not covered say: "This topic was not covered in the lecture." """

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = ask_ollama(prompt)
                st.write(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()

        # Regular chat input
        if question := st.chat_input("Ask a question about the lecture..."):
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)

            relevant = find_relevant_blocks(question, notes)
            context  = "\n\n".join([
                f"[{r['start_time']}s-{r['end_time']}s]: {r['notes']}"
                for r in relevant
            ])
            prompt = f"""You are a helpful study assistant.
Lecture notes context:
{context}

Student question: {question}

Answer clearly based only on the lecture content above.
If not covered say: "This topic was not covered in the lecture." """

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = ask_ollama(prompt)
                st.write(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})

        # Clear chat
        if st.session_state.messages:
            st.divider()
            if st.button("🗑️ Clear chat history", use_container_width=True):
                st.session_state.messages = []
                st.rerun()