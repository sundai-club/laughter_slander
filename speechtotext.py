import whisper
import time
import os
from pydub import AudioSegment

def load_and_transcribe(audio_files):
    # Load the Whisper model
    model = whisper.load_model("base")

    results = []
    for file in audio_files:
        # Start timing the transcription process
        start_time = time.time()

        # Load the audio file and transcribe
        result = model.transcribe(file)

        # Calculate transcription time
        elapsed_time = time.time() - start_time

        # Load audio to get duration using pydub (requires ffmpeg)
        audio = AudioSegment.from_file(file)
        length_seconds = len(audio) / 1000

        # Store result and metadata
        results.append({
            'file': file,
            'transcription': result["text"],
            'transcription_time': elapsed_time,
            'audio_length': length_seconds
        })

        print(f"File: {file}")
        print(f"Transcription: {result['text']}")
        print(f"Transcription took: {elapsed_time:.2f} seconds")
        print(f"Length of audio: {length_seconds} seconds\n")

    return results

# List of audio files
audio_files = ["test_audio.mp3"]  # Add more files as needed

# Run the transcription function
transcriptions = load_and_transcribe(audio_files)
