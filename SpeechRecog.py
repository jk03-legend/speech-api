from flask import Flask, request, jsonify
import speech_recognition as sr
import os

app = Flask(__name__)
recognizer = sr.Recognizer()

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    try:
        with sr.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration=0.2)
            audio = recognizer.listen(mic)

            text = recognizer.recognize_google(audio)
            text = text.lower()
            return jsonify({"text": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 1000)))
