from flask import Flask, request, jsonify
import speech_recognition as sr
from flask_cors import CORS
import hashlib
import spacy
from textblob import TextBlob

app = Flask(__name__)
CORS(app)

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

cache = {}

def get_audio_hash(audio_bytes):
    """Generate a stable hash for the audio content."""
    return hashlib.md5(audio_bytes).hexdigest()

def process_text(text):
    """Perform NLP tasks on recognized text."""
    doc = nlp(text)

    # Named Entity Recognition (NER)
    entities = {ent.text: ent.label_ for ent in doc.ents}

    # Sentiment Analysis
    sentiment = TextBlob(text).sentiment.polarity  # Range: -1 (negative) to 1 (positive)
    sentiment_label = "positive" if sentiment > 0 else "negative" if sentiment < 0 else "neutral"

    return {"text": text, "entities": entities, "sentiment": sentiment_label}

@app.route('/recognize', methods=['POST'])
def recognize_speech():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['file']
    audio_bytes = file.read()
    audio_hash = get_audio_hash(audio_bytes)

    if audio_hash in cache:
        return jsonify(cache[audio_hash])

    file.seek(0)
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(file) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.record(source, duration=None)
        
        results = recognizer.recognize_google(audio, language="en-US", show_all=True)

        if results and "alternative" in results:
            text = results["alternative"][0]["transcript"]
        else:
            return jsonify({"error": "Could not understand audio"}), 400

        processed_text = process_text(text)
        cache[audio_hash] = processed_text

        return jsonify(processed_text)
    
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service unavailable"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
