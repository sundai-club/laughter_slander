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

    # Initialize lists to store start and end times
    start_times = []
    end_times = []

    # Iterate over each dictionary in the list
    for item in timestamps:
        item['start'] = item['start']*1000
        item['end'] = item['end']*1000
        start_times.append(item['start'])
        end_times.append(item['end'])

    # Parse audio at each timestamp
    segments = []
    for timestamp in end_times:
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
audio_path = "./test_audio.mp3"
timestamps = [{'filename': './tst_wave/laugh_0.wav', 'start': 15.365865142088449, 'end': 16.115419539263495}, {'filename': './tst_wave/laugh_1.wav', 'start': 19.34787287708088, 'end': 41.71738691777367}, {'filename': './tst_wave/laugh_2.wav', 'start': 52.1877249033126, 'end': 53.10124432486969}, {'filename': './tst_wave/laugh_3.wav', 'start': 69.0058516899277, 'end': 73.62029594753658}, {'filename': './tst_wave/laugh_4.wav', 'start': 80.29601479737684, 'end': 86.31587354968893}, {'filename': './tst_wave/laugh_5.wav', 'start': 88.84561964015471, 'end': 101.86912729107114}, {'filename': './tst_wave/laugh_6.wav', 'start': 105.68717000168154, 'end': 118.19535900454012}, {'filename': './tst_wave/laugh_7.wav', 'start': 119.43680847486128, 'end': 125.33954935261478}, {'filename': './tst_wave/laugh_8.wav', 'start': 131.85130317807298, 'end': 133.7251891710106}]

parse_audio_at_timestamps(audio_path, timestamps)

# If you want to play a segment (requires simpleaudio library)
# parsed_segments[0].export("temp.wav", format="wav")
# import simpleaudio as sa
# wave_obj = sa.WaveObject.from_wave_file("temp.wav")
# play_obj = wave_obj.play()
# play_obj.wait_done()