from flask import Flask, request, jsonify
import speech_recognition as sr
from flask_cors import CORS
import hashlib

app = Flask(__name__)
CORS(app)

cache = {}

def get_audio_hash(audio_bytes):
    """Generate a stable hash for the audio content."""
    return hashlib.md5(audio_bytes).hexdigest()

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    audio_bytes = file.read()

    audio_hash = get_audio_hash(audio_bytes)

    if audio_hash in cache:
        return jsonify({"text": cache[audio_hash]})

    file.seek(0)  # Reset file pointer
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(file) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for noise
            audio = recognizer.record(source, duration=None)  # Capture full audio
        
        # Get detailed results for better accuracy
        results = recognizer.recognize_google(audio, language="en-US", show_all=True)

        if results and "alternative" in results:
            text = results["alternative"][0]["transcript"]  # Pick most confident result
        else:
            return jsonify({"error": "Could not understand audio"}), 400

        cache[audio_hash] = text  # Store recognized text in cache
        return jsonify({"text": text})
    
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service unavailable"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
