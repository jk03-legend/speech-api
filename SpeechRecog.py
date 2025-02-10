import os
import speech_recognition as sr
from flask import Flask, request, jsonify
from google.cloud import speech
from flask_cors import CORS
import whisper

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "your-service-account.json"

app = Flask(__name__)
CORS(app)

client = speech.SpeechClient()
model = whisper.load_model("base")

@app.route('/stream', methods=['POST'])
def stream_speech():
    file = request.files['file']
    audio = whisper.load_audio(file)
    text = model.transcribe(audio)["text"]
    return jsonify({"text": text})

@app.route('/stream', methods=['POST'])
def stream_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    audio_data = file.read()

    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="en-US"
    )

    response = client.recognize(config=config, audio=audio)
    
    if response.results:
        text = response.results[0].alternatives[0].transcript
        return jsonify({"text": text})
    else:
        return jsonify({"error": "No speech detected"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
