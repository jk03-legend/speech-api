#!/bin/bash
pip install -r requirements.txt

mkdir -p models

if [ ! -d "models/vosk-model-en-us" ]; then
    echo "Downloading VOSK model..."
    wget -O vosk-model.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model.zip -d models
    mv models/vosk-model-small-en-us-0.15 models/vosk-model-en-us
    rm vosk-model.zip
fi
