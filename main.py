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


def transcribe_audio_from_directory(directory_path):
    """
    @julie: Take in a directory path and transcribe all audio files in that directory. return in json format
    """

    # Load the Whisper model
    model = whisper.load_model("base")
    
    # Prepare to collect results
    results = []
    
    # List all files in the given directory
    audio_files = [f for f in os.listdir(directory_path) if f.endswith('.mp3') or f.endswith('.wav')]
    
    # Process each audio file in the directory
    for filename in audio_files:
        file_path = os.path.join(directory_path, filename)
        
        # Start timing the transcription process
        start_time = time.time()

        # Load the audio file and transcribe
        result = model.transcribe(file_path)

        # Calculate transcription time
        elapsed_time = time.time() - start_time

        # Load audio to get duration using pydub (requires ffmpeg)
        audio = AudioSegment.from_file(file_path)
        length_seconds = len(audio) / 1000

        # Store result and metadata
        results.append({
            'file': filename,
            'transcription': result["text"],
            'transcription_time': elapsed_time,
            'audio_length': length_seconds
        })

        print(f"File: {filename}")
        print(f"Transcription: {result['text']}")
        print(f"Transcription took: {elapsed_time:.2f} seconds")
        print(f"Length of audio: {length_seconds} seconds\n")

    # Convert results to JSON format
    return json.dumps(results, indent=2)

def truncate_jokes(text) -> str:
    """
    @julie: Truncate jokes in the text to a certain length, given a truncated transcription
    """
    # Hypothetical function to truncate jokes
    # Replace with actual implementation
    return text[:1000]

# testing
transcriptions_json = transcribe_audio_from_directory("audio_chunks/task_id_0/")
print(transcriptions_json)

if __name__ == '__main__':
    app.run(debug=True)
    
