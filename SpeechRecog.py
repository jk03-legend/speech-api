import speech_recognition as sr
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import whisper
model = whisper.load_model("base")

@app.route('/stream', methods=['POST'])
def stream_speech():
    file = request.files['file']
    audio = whisper.load_audio(file)
    text = model.transcribe(audio)["text"]
    return jsonify({"text": text})
    
@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(file) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language="en-US", show_all=False)  # Change language if needed
        return jsonify({"text": text})
    
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
