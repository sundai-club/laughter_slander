from openai import OpenAI
from tqdm import tqdm
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the Whisper model
model = "whisper-1"

# Specify the folder containing audio files
audio_folder = "data"

# Get a list of all segment files in the folder
segment_files = sorted([f for f in os.listdir(audio_folder) if f.startswith("segment_") and f.endswith(".mp3")])

# Initialize an empty list to store all transcriptions
all_transcriptions = []

# Process each audio file
for segment_file in tqdm(segment_files, desc="Transcribing"):
    # Full path to the audio file
    audio_path = os.path.join(audio_folder, segment_file)
    
    audio_file= open(audio_path, "rb")
    
    # Get the transcription text
    transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                    )
                    
    # Add the transcription to our list
    all_transcriptions.append(transcription.text)

    all_transcriptions.append("[laughter]")

# Combine all transcriptions into a single string
full_transcription = " ".join(map(str, all_transcriptions))

# Save the full transcription to a text file
output_file = "full_transcription.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(full_transcription)

print(f"Transcription complete! Full transcription saved to {output_file}")