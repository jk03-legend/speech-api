from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment, silence

app = Flask(__name__)

def remove_silence(audio_file):
    audio = AudioSegment.from_file(audio_file)
    trimmed_audio = silence.split_on_silence(audio, silence_thresh=-40)
    
    if len(trimmed_audio) == 0:
        return None  # No speech detected

    final_audio = trimmed_audio[0]  # Use the first segment with speech
    final_audio.export("trimmed.wav", format="wav")
    return "trimmed.wav"

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    trimmed_file = remove_silence(file)

    if not trimmed_file:
        return jsonify({"error": "No speech detected"}), 400

    recognizer = sr.Recognizer()
    with sr.AudioFile(trimmed_file) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Noise reduction
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return jsonify({"text": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
