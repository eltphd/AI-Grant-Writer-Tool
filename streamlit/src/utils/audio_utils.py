"""Audio transcription utilities for the Streamlit front‑end.

These helpers rely on the open‑source Whisper model to convert uploaded
audio files into text.  The resulting transcription can then be stored in
the database just like manually entered text for use in RAG retrieval.

Note: To use these functions you must install the `openai-whisper`
package in your environment.  Whisper is relatively compute heavy; for
production use consider leveraging a hosted transcription service.
"""

from typing import IO, Optional

try:
    import whisper  # type: ignore
except ImportError:
    whisper = None  # type: ignore


def transcribe_audio(file: IO[bytes], model_name: str = "base") -> Optional[str]:
    """Transcribe an audio file to text using Whisper.

    Args:
        file: A file‑like object containing audio data (wav, mp3, etc.).
        model_name: Which Whisper model size to load (e.g. 'base', 'medium', 'large').

    Returns:
        The transcribed text, or None if transcription failed.
    """
    if whisper is None:
        print("Whisper library is not installed; cannot transcribe audio.")
        return None
    try:
        # Load the specified model once.  For repeated calls you may want to
        # cache the model globally.
        model = whisper.load_model(model_name)
        # Whisper expects a path; if a file‑like object is provided we need
        # to read it into memory.  Here we assume the file supports
        # read().  In Streamlit, file_uploader returns an UploadedFile
        # object with getvalue().
        audio_bytes = file.read() if hasattr(file, "read") else file
        result = model.transcribe(audio_bytes)
        return result.get("text")
    except Exception as e:
        print(f"ERROR transcribe_audio: {e}")
        return None