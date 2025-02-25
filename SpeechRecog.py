from flask import Flask, request, jsonify
import speech_recognition as sr
from flask_cors import CORS
import vosk
import json
import wave
import os

app = Flask(__name__)
CORS(app)

# Load VOSK model
MODEL_PATH = "models/vosk-model-en-us"
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Model path {MODEL_PATH} not found! Download a VOSK model.")

vosk_model = vosk.Model(MODEL_PATH)

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    file_path = "temp.wav"
    file.save(file_path)

    wf = wave.open(file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return jsonify({"error": "Audio file must be WAV format, 16-bit PCM"}), 400

    rec = vosk.KaldiRecognizer(vosk_model, wf.getframerate())
    result = ""
    
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())["text"]

    os.remove(file_path)  # Clean up temp file

    return jsonify({"text": result.strip() if result else "No speech detected"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
