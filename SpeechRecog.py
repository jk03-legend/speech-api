import speech_recognition as sr
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment, silence

app = Flask(__name__)
CORS(app)

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(file) as source:
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300  # Adjust to ignore background noise
            recognizer.dynamic_energy_threshold = True  # Auto adjust noise threshold
            audio = recognizer.record(source, duration=5)  # Limit recording to 5 sec
            audio = AudioSegment.from_file(file)
            trimmed_audio = silence.split_on_silence(audio, silence_thresh=-40)
            trimmed_audio.export("trimmed.wav", format="wav")
    
        text = recognizer.recognize_google(trimmed_audio, language="en-US", show_all=False)  # Change language if needed
        return jsonify({"text": text})
    
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
