from flask import Flask, request, jsonify
import speech_recognition as sr
from flask_cors import CORS
from gtts import gTTS

app = Flask(__name__)
CORS(app)

cache = {}

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    audio_hash = hash(file.read())

    if audio_hash in cache:
        return jsonify({"text": cache[audio_hash]})

    file.seek(0)
    recognizer = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        audio_tts = generate_tts(text)
        cache[audio_hash] = text    
        return jsonify({"text": text, "audio_url": audio_tts})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_tts(text):
    tts = gTTS(text=text, lang='en')
    audio_filename = "response.mp3"
    audio_path = os.path.join("static", audio_filename)
    tts.save(audio_path)
    return f"/static/{audio_filename}"


@app.route('/static/<filename>')
def serve_audio(filename):
    return send_file(os.path.join("static", filename), mimetype="audio/mpeg")


if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)

