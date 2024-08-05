from pydub import AudioSegment
import os

from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env')

def parse_audio_at_timestamps(audio_path, timestamps, duration=30000):
    """
    Parse an audio file at given timestamps.
    
    :param audio_path: Path to the audio file
    :param timestamps: List of timestamps in milliseconds
    :param duration: Duration of each segment in milliseconds (default: 1000ms)
    :return: List of audio segments
    """
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)

    # Initialize lists to store start and end times
    start_times = []
    end_times = []

    # Iterate over each dictionary in the list
    for item in timestamps:
        item['start'] = item['start'] * 1000
        item['end'] = item['end'] * 1000
        start_times.append(item['start'])
        end_times.append(item['end'])

    # Parse audio at each timestamp
    segments = []
    for timestamp in start_times:
        # Extract segment
        if timestamp - duration < 0:
            segment = audio[0:timestamp]
        else:
            segment = audio[timestamp - duration:timestamp]
        segments.append(segment)
    
    
    folder_name = "data"
    # Check if the folder exists
    if not os.path.exists(folder_name):
        # If it doesn't exist, create it
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created.")

    # If you want to save the parsed segments
    for i, segment in enumerate(segments):
        segment.export(f"{folder_name}/segment_{i}.mp3", format="mp3")
        print(f"{folder_name}/segment_{i}.mp3 saved!")

# Example usage