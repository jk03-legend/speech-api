from flask import Flask, request, jsonify
import speech_recognition as sr
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow Unity to access API
recognizer = sr.Recognizer()

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    
    try:
        with sr.AudioFile(file) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return jsonify({"text": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 1000)))
