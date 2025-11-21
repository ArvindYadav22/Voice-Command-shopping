Voice Shopping Assistant
========================


Short, practical guide to run a voice- and chat-enabled shopping assistant with Streamlit and Gradio frontends backed by a FastAPI API. Users can browse products, manage a cart, type messages, or speak commands that are transcribed and processed by the backend.

Features
- Browse items grouped by category
- Persistent cart management
- Text chat with the assistant
- Voice command input (file upload in Streamlit; microphone capture in Gradio)

Architecture
- Backend: FastAPI app exposes endpoints for chat, voice transcription, items, and cart operations.
- Frontends:
  - Streamlit: text chat UI and audio file upload for voice.
  - Gradio: text chat UI and live microphone capture with browser permissions.
- Data: simple JSON-based products and carts; Chroma vector store for retrieval tasks.

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

Run the Gradio App (text chat + microphone)
```
python gradio_app.py
```



API Endpoints (summary)
- GET /items_dropdown: grouped items for the UI
- GET /cart: current cart contents
- POST /chat { text }: returns assistant reply and updated cart
- POST /voice-chat (multipart/form-data audio_file): transcribes audio, returns reply and cart

Configuration
- Default backend URL is http://127.0.0.1:8000 (see BACKEND_URL in streamlit_app.py and gradio_app.py)
- Ensure the backend is running before launching the UI

Environment Variables
- Create a .env file if required by your providers or embeddings (see app/config.py), for example:
```
OPENAI_API_KEY=your_key
```

Troubleshooting
- On first install, large wheels (torch/torchaudio) can take time to download.
- If microphone access is blocked, allow mic permissions for the Gradio URL.
- If package installs fail on Windows, ensure Python 3.10 is in PATH and upgrade pip:
  `python -m pip install --upgrade pip setuptools wheel`.

Notes
- Some packages (e.g., torch/torchaudio) are large; first install may take time
- If microphone access is blocked in the browser, allow mic permissions for the Gradio URL


