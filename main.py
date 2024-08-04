import json
import os
import tempfile
import time
import uuid
from flask import Flask, request, jsonify
from threading import Thread
from time import sleep
import whisper
import time
import os
from pydub import AudioSegment

app = Flask(__name__)

tasks = {}


def process_audio(file_path, task_id):
    sleep(1)  # Simulate a long-running process
    laughter_data = detect_laughter(file_path)
    laughter_transcriptions = []

    for laughter_data_timestamp in laughter_data:
        laughter_transcriptions.append(transcribe_audio(file_path, laughter_data_timestamp))

    tasks[task_id]['status'] = 'completed'
    tasks[task_id]['result'] = {
        "laughter_timestamps": laughter_data,
        "laughter_transcriptions": laughter_transcriptions
    }


@app.route('/upload', methods=['POST'])
def upload_mp3():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and (file.filename.endswith('.mp3') or file.filename.endswith('.mp4')):
        task_id = str(uuid.uuid4())
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)

        tasks[task_id] = {'status': 'processing', 'result': None}

        thread = Thread(target=process_audio, args=(file_path, task_id))
        thread.start()

        return jsonify({"task_id": task_id}), 200

    return jsonify({"error": "Invalid file format"}), 400


@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Invalid task ID"}), 400

    if task['status'] == 'completed':
        return jsonify(task['result']), 200

    return jsonify({"status": task['status']}), 200


def detect_laughter(file_path) -> list[float]:
    """
    Detect laughter timestamps in an audio file
    :param file_path: the path to the audio file
    :return: a list of timestamps where laughter is detected
    """
    # Hypothetical function to detect laughter timestamps
    # Replace with actual implementation
    return [5.0, 15.2, 22.5]

def transcribe_audio(file_path, laughter_data_timestamp):
    # @julie: use transcribe_audio_from_directory as a helper function. integrate it or make modifications when integrating
    # Hypothetical function to transcribe audio
    # Replace with actual implementation
    return "This is a sample transcription with laughter at the given point!!"

def audio_to_transcription_and_timestamp(path_to_conversion):
    """
    @julie: Take in a path to file to be converted (mp3/wav) and return json containing transcription and timestamps.
    input:
    - path_to_conversion: path to the directory containing **1 only** audio file
    return:
    - a JSON
    - json.text -> transcription
    - json.segments -> list of token(word or terms) and timestamps
    """

    # Load the Whisper model
    model = whisper.load_model("base")

    # Start timing the transcription process
    start_time = time.time()

    # Load the audio file and transcribe
    result = model.transcribe(path_to_conversion, word_timestamps=True)

    # Calculate transcription time
    elapsed_time = time.time() - start_time

    # Load audio to get duration using pydub (requires ffmpeg)
    audio = AudioSegment.from_file(path_to_conversion)
    length_seconds = len(audio) / 1000

    # Store result and metadata
    transcription_result = {
        'file': path_to_conversion,
        'transcription': result["text"],
        'transcription_time': elapsed_time,
        'audio_length': length_seconds
    }

    print(f"File: {path_to_conversion}")
    print(f"Transcription: {result}")
    print(f"Transcription took: {elapsed_time:.2f} seconds")
    print(f"Length of audio: {length_seconds} seconds\n")

    return transcription_result


def truncate_jokes(text) -> str:
    """
    @julie: Truncate jokes in the text to a certain length, given a truncated transcription
    """
    # Hypothetical function to truncate jokes
    # Replace with actual implementation
    return text[:1000]

# TODO: remove this. Testing: Run the transcription function
transcriptions = audio_to_transcription_and_timestamp("test_audio.mp3")
print(transcriptions)


if __name__ == '__main__':
    print('Launching flask server...')
    app.run(debug=True, host='0.0.0.0', port=8000)
    
