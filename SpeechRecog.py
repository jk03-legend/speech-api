from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# OpenAI API Key
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    file_path = "temp.wav"
    file.save(file_path)

    # Read and send the audio file to OpenAI Whisper API
    try:
        with open(file_path, "rb") as audio_file:
            response = openai.Audio.transcribe(
                model="whisper-1", 
                file=audio_file
            )
            transcript = response.get("text", "")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(file_path)  # Clean up temp file

    return jsonify({"text": transcript.strip() if transcript else "No speech detected"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
