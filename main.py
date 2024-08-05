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
from src.laughter_detection import detect_laughter
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import json

# Locate the .env file and load environment variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI()

app = Flask(__name__)

tasks = {}


def combine_laughter_and_transcript(laughter_data, whisper_transcriptions):
    # Extract the text and segments from whisper_transcriptions
    transcript = whisper_transcriptions['text']
    segments = whisper_transcriptions['segments']

    # Create a list to store all events (speech and laughter)
    all_events = []

    # Add speech segments to all_events
    for segment in segments:
        all_events.append({
            'type': 'speech',
            'start': segment['start'],
            'end': segment['end'],
            'text': segment['text']
        })


    # Add laughter events to all_events
    for laugh in laughter_data:
        start = laugh['start']
        end = laugh['end']
        duration = end - start
        num_laughs = int(duration)  # One [Laughter] tag per second
        all_events.append({
            'type': 'laughter',
            'start': start,
            'end': end,
            'text': '[Laughter]'
        })

        # for i in range(num_laughs):
        #     all_events.append({
        #         'type': 'laughter',
        #         'start': start + i,
        #         'end': start + i + 1,
        #         'text': '[Laughter]'
        #     })

    # Sort all events by start time
    all_events.sort(key=lambda x: x['start'])

    # Combine events into a single transcript
    combined_transcript = []
    for event in all_events:
        timestamp = f"[{event['start']:.2f}-{event['end']:.2f}]"
        combined_transcript.append(f"{timestamp} {event['text']}")

    return "\n".join(combined_transcript)

def process_audio(file_path, task_id):
  
  # Combine transcript
  laughter_data = detect_laughter(file_path)

  whisper_transcriptions = audio_to_transcription_and_timestamp(file_path)

  combined_transcript = combine_laughter_and_transcript(laughter_data, whisper_transcriptions)
  print(combined_transcript)
  
  # Pass to LLM
  import json
  prompt = "Here is the combined transcript for our conversation " + combined_transcript + " It's your job to chunk it into funny segments. Some segments may have multiple laughter interruptions within them. Each segment should include earlier parts of transcript that are relevant to make it maximally funny. For each segment, output a json object with {startTimeStamp: , endTimeStamp: , text: }. Only output a list of json objects."
  response = client.chat.completions.create(
      model="gpt-4o",
      messages=[{"role": "user", "content": prompt}],
  )
  chat_response = response.choices[0].message.content
  chat_response = cleaned_string = chat_response.strip().removeprefix('```json').removesuffix('```')
  print(chat_response)

  # Parse response into json and, calculate duration and return
  if chat_response:
      try:
          json_list = json.loads(chat_response)
          for json_obj in json_list:
            start_time = json_obj.get('startTimeStamp')
            end_time = json_obj.get('endTimeStamp')
            
            if start_time is not None and end_time is not None:
              # Convert timestamps to floats before subtraction
              duration_sec = float(end_time) - float(start_time)  
              json_obj['durationSec'] = duration_sec
              json_obj['startSec'] = start_time

          print(json_list)
          return json_list
      except json.JSONDecodeError as e:
          print(f"Error decoding JSON: {e}")
          json_list = []
          return json_list
  else:
      json_list = []
      print("GPT model returned an empty response.")
      return json_list
  

    # tasks[task_id]['status'] = 'completed'
    # tasks[task_id]['result'] = {
    #     "laughter_timestamps": laughter_data,
    #     "laughter_transcriptions": laughter_transcriptions
    # }

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

        return jsonify({"taskId": task_id}), 200

    return jsonify({"error": "Invalid file format"}), 400


@app.route('/status/<taskId>', methods=['GET'])
def get_status(taskId):
    task = tasks.get(taskId)
    if not task:
        return jsonify({"error": "Invalid task ID"}), 400

    if task['status'] == 'completed':
        return jsonify(task['result']), 200

    return jsonify({"status": task['status']}), 200


def detect_laughter(file_path) -> dict:
    """
    Detect laughter timestamps in an audio file
    :param file_path: the path to the audio file
    :return: a list of timestamps where laughter is detected
    """
    # Hypothetical function to detect laughter timestamps
    # Replace with actual implementation
    outputs = detect_laughter(file_path)
    outputs = [x__dict__ for x in outputs]
    return outputs


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
# transcriptions = audio_to_transcription_and_timestamp("test_audio.mp3")
# print(transcriptions)

if __name__ == '__main__':
    print('Launching flask server...')
    app.run(debug=True, host='0.0.0.0', port=8000)
