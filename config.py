import os

weights_path = "GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s2G2333k.pth"
api_url = "http://127.0.0.1:9880"  # Your SoVITS-API host/port
base_path = os.path.dirname(os.path.abspath(__file__))


# Define the model to use for Ollama
# You can change this to any model available in your Ollama installation
model = "gemma2:9b"