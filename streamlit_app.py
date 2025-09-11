import requests
import streamlit as st
import tempfile
import os




BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Voice Shopping Assistant", layout="wide")


st.sidebar.title(" Shopping Assistant")


try:
    items_resp = requests.get(f"{BACKEND_URL}/items_dropdown")
    items_resp.raise_for_status()
    items_data = items_resp.json().get("categories", [])
except Exception:
    items_data = []

for category in items_data:
    with st.sidebar.expander(category["category"].title()):
        for item in category["items"]:
            st.write(f"{item['name']} - ₹{item['price']} ({item['unit']})")


cart = st.session_state.get("cart")
if cart is None:
    try:
        cart_resp = requests.get(f"{BACKEND_URL}/cart")
        cart_resp.raise_for_status()
        cart = cart_resp.json()
    except Exception:
        cart = {"items": [], "total": 0.0}
    st.session_state["cart"] = cart


with st.sidebar.expander(" Your Cart", expanded=True):
    items = cart.get("items", []) if isinstance(cart, dict) else []
    total = cart.get("total", 0.0) if isinstance(cart, dict) else 0.0
    if items:
        for it in items:
            name = it.get("name")
            qty = it.get("quantity")
            price = it.get("price")
            subtotal = it.get("subtotal")
            unit = it.get("unit") or ""
            st.write(f"- {name} x{qty} @ ₹{price} {unit} — ₹{subtotal}")
        st.markdown(f"**Total: ₹{total}**")
    else:
        st.write("Cart is empty.")


st.title("Chat Shopping Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


st.subheader(" Available Items")
if items_data:
    for category in items_data:
        with st.expander(f" {category['category'].title()}", expanded=False):
            for item in category["items"]:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{item['name']}**")
                with col2:
                    st.write(f"₹{item['price']}")
                with col3:
                    st.write(f"per {item['unit']}")
else:
    st.info("No items available. Please check if the backend is running.")

st.divider()

st.subheader("Voice Command (Upload)")
uploaded_audio = st.file_uploader(
    "Upload an audio file (wav/mp3/m4a/ogg/webm)",
    type=["wav", "mp3", "m4a", "ogg", "webm"],
    accept_multiple_files=False,
    help="Upload a short voice command to transcribe and execute"
)

if uploaded_audio is not None:
    try:
        suffix = os.path.splitext(uploaded_audio.name)[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_audio.getbuffer())
            temp_file_path = temp_file.name

        with open(temp_file_path, "rb") as audio_file:
            files = {"audio_file": (uploaded_audio.name, audio_file, "application/octet-stream")}
            resp = requests.post(f"{BACKEND_URL}/voice-chat", files=files, timeout=60)
            resp.raise_for_status()
            data = resp.json()

        if data.get("success"):
            transcribed_text = data.get("transcribed_text", "")
            chat_response = data.get("chat_response", {})
            reply = chat_response.get("reply", "")
            cart = chat_response.get("cart", {"items": [], "total": 0.0})

            st.session_state.messages.append({"role": "user", "content": transcribed_text})
            with st.chat_message("user"):
                st.markdown(transcribed_text)

            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)

            st.session_state["cart"] = cart
            st.rerun()
        else:
            st.error("Could not process voice input. Please try again.")
    except Exception as e:
        st.error(f"Error processing voice input: {str(e)}")
    finally:
        try:
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        except Exception:
            pass

st.divider()

st.subheader("Chat with Assistant")


if user_input := st.chat_input("Type your message here..."):
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        resp = requests.post(f"{BACKEND_URL}/chat", json={"text": user_input}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        reply = data.get("reply", "")
        cart = data.get("cart", {"items": [], "total": 0.0})
    except Exception:
        reply = " Error: Could not reach backend."
        cart = {}

    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

  
    st.session_state["cart"] = cart



