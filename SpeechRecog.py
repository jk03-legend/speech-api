from flask import Flask, request, jsonify
import torch
import whisper
import hashlib
import tempfile

app = Flask(__name__)

# Load the Whisper model (Choose 'tiny', 'base', 'small', 'medium', or 'large-v2' for best accuracy)
MODEL_SIZE = "small"  # Change to "large-v2" for best accuracy
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model(MODEL_SIZE, device=device)

cache = {}

def get_audio_hash(file):
    """Generate a unique hash for an audio file."""
    hasher = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b""):
        hasher.update(chunk)
    file.seek(0)  # Reset file pointer
    return hasher.hexdigest()

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    audio_hash = get_audio_hash(file)

    if audio_hash in cache:
        return jsonify({"text": cache[audio_hash]})

    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_audio:
        file.save(temp_audio.name)

        # Run Whisper transcription
        result = model.transcribe(temp_audio.name)
    
    text = result['text'].strip()
    cache[audio_hash] = text  # Store in cache

    return jsonify({"text": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
