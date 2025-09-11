Voice Shopping Assistant
========================

Demo video: https://youtu.be/fTVNupzqroQ

Short, practical guide to run a voice- and chat-enabled shopping assistant with both Streamlit and Gradio frontends backed by a FastAPI API.

Features
- Browse items grouped by category
- Persistent cart management
- Text chat with the assistant
- Voice command input (file upload in Streamlit; microphone capture in Gradio)

Project Structure
```
.
├─ app/
│  ├─ __init__.py
│  ├─ audio_service.py
│  ├─ cart.py
│  ├─ chatbot.py
│  ├─ config.py
│  ├─ main.py
│  ├─ models.py
│  ├─ products.py
│  ├─ routes.py
│  └─ vectorstore.py
├─ data/
│  └─ chroma/
├─ logs/
│  └─ cart.log
├─ carts.json
├─ products.json
├─ requirements.txt
├─ streamlit_app.py
├─ gradio_app.py
└─ test_voice_integration.py
```

Prerequisites
- Python 3.10
- Windows PowerShell or a terminal

Setup
```
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

Run the Backend (FastAPI)
```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Run the Streamlit App (text chat + audio upload)
```
streamlit run streamlit_app.py
```

Run the Gradio App (text chat + microphone)
```
python gradio_app.py
```

Configuration
- Default backend URL is http://127.0.0.1:8000 (see BACKEND_URL in streamlit_app.py and gradio_app.py)
- Ensure the backend is running before launching the UI

Notes
- Some packages (e.g., torch/torchaudio) are large; first install may take time
- If microphone access is blocked in the browser, allow mic permissions for the Gradio URL


