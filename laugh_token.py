from pydub import AudioSegment
import os

def parse_audio_at_timestamps(audio_path, timestamps, duration=60000):
    """
    Parse an audio file at given timestamps.
    
    :param audio_path: Path to the audio file
    :param timestamps: List of timestamps in milliseconds
    :param duration: Duration of each segment in milliseconds (default: 1000ms)
    :return: List of audio segments
    """
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)

    # Parse audio at each timestamp
    segments = []
    for timestamp in timestamps:
        # Extract segment
        segment = audio[timestamp-duration:timestamp]
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

# Example usage
audio_path = "/Users/cozyshu/Desktop/test_audio.mp3"
timestamps = [61000, 90000]  # Timestamps in milliseconds

parse_audio_at_timestamps(audio_path, timestamps)




# If you want to play a segment (requires simpleaudio library)
# parsed_segments[0].export("temp.wav", format="wav")
# import simpleaudio as sa
# wave_obj = sa.WaveObject.from_wave_file("temp.wav")
# play_obj = wave_obj.play()
# play_obj.wait_done()