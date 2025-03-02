from flask import Flask, request, jsonify
import speech_recognition as sr
from flask_cors import CORS
import torch
import hashlib
import random
import json
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

app = Flask(__name__)
CORS(app)

# Load NLP chatbot data
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"
cache = {}

def get_audio_hash(audio_bytes):
    """Generate a stable hash for the audio content."""
    return hashlib.md5(audio_bytes).hexdigest()

def chatbot_response(text):
    """Process text through the chatbot and return a response."""
    sentence = tokenize(text)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    return "I do not understand..."

@app.route('/recognize_chat', methods=['POST'])
def recognize_speech_chat():
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

        # Convert Speech to Text
        results = recognizer.recognize_google(audio, language="en-US", show_all=True)

        if results and "alternative" in results:
            text = results["alternative"][0]["transcript"]
        else:
            return jsonify({"error": "Could not understand audio"}), 400

        # Get Chatbot Response
        bot_reply = chatbot_response(text)

        response = {"user_text": text, "bot_reply": bot_reply}
        cache[audio_hash] = response  # Cache response for faster retrieval

        return jsonify(response)

    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service unavailable"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
