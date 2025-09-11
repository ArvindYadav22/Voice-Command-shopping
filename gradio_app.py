import gradio as gr
import requests
import tempfile
import os
import soundfile as sf

BACKEND_URL = "http://127.0.0.1:8000"


def fetch_items():
    try:
        resp = requests.get(f"{BACKEND_URL}/items_dropdown", timeout=15)
        resp.raise_for_status()
        return resp.json().get("categories", [])
    except Exception:
        return []


def fetch_cart():
    try:
        resp = requests.get(f"{BACKEND_URL}/cart", timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"items": [], "total": 0.0}


def render_items_markdown(categories):
    if not categories:
        return "No items available. Ensure backend is running."
    lines = ["Categories"]
    for cat in categories:
        lines.append(
            f"<details><summary style='cursor:pointer; font-weight:600;'>{cat['category'].title()}</summary>"
        )
        if cat.get("items"):
            lines.append("<ul style='margin-top:8px;'>")
            for item in cat.get("items", []):
                lines.append(
                    f"<li><strong>{item['name']}</strong> — ₹{item['price']} per {item['unit']}</li>"
                )
            lines.append("</ul>")
        lines.append("</details>")
    return "\n".join(lines)


def render_cart_markdown(cart):
    items = cart.get("items", []) if isinstance(cart, dict) else []
    total = cart.get("total", 0.0) if isinstance(cart, dict) else 0.0
    lines = ["Your Cart"]
    if not items:
        lines.append("Cart is empty.")
    else:
        for it in items:
            name = it.get("name")
            qty = it.get("quantity")
            price = it.get("price")
            subtotal = it.get("subtotal")
            unit = it.get("unit") or ""
            lines.append(f"- {name} x{qty} @ ₹{price} {unit} — ₹{subtotal}")
        lines.append(f"\nTotal: ₹{total}")
    return "\n".join(lines)


def send_text_chat(history, user_text):
    history = history or []
    if not user_text:
        return history, gr.update()
    try:
        resp = requests.post(f"{BACKEND_URL}/chat", json={"text": user_text}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        reply = data.get("reply", "")
        cart = data.get("cart", {"items": [], "total": 0.0})
    except Exception:
        reply = "Error: Could not reach backend."
        cart = {"items": [], "total": 0.0}

    history = history + [(user_text, reply)]
    cart_md = render_cart_markdown(cart)
    return history, cart_md


def send_voice_chat(history, audio):
    history = history or []
    if audio is None:
        return history, gr.update()
    sample_rate, data = audio

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            sf.write(f.name, data, sample_rate)
            tmp_path = f.name
        with open(tmp_path, "rb") as af:
            files = {"audio_file": ("audio.wav", af, "audio/wav")}
            r = requests.post(f"{BACKEND_URL}/voice-chat", files=files, timeout=60)
            r.raise_for_status()
            data = r.json()
    finally:
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception:
            pass

    if data.get("success"):
        transcribed_text = data.get("transcribed_text", "")
        chat_response = data.get("chat_response", {})
        reply = chat_response.get("reply", "")
        cart = chat_response.get("cart", {"items": [], "total": 0.0})
        history = history + [(transcribed_text, reply)]
        cart_md = render_cart_markdown(cart)
        return history, cart_md
    else:
        history = history + [("(voice)", "Could not process voice input.")]
        return history, gr.update()


def refresh_sidebar():
    categories = fetch_items()
    items_md = render_items_markdown(categories)
    cart = fetch_cart()
    cart_md = render_cart_markdown(cart)
    return items_md, cart_md


with gr.Blocks(title="Shopping Assistant", css=".gradio-container {max-width: 1200px !important}") as demo:
    gr.Markdown("# Shopping Assistant")
    with gr.Row():
        with gr.Column(scale=1, min_width=320):
            gr.Markdown("### Browse Items")
            sidebar_items = gr.Markdown(value="Loading items...", elem_id="items_md")
            gr.Markdown("---")
            sidebar_cart = gr.Markdown(value="Loading cart...", elem_id="cart_md")
            with gr.Row():
                refresh_btn = gr.Button("Refresh", variant="secondary")
        with gr.Column(scale=3):
            chat = gr.Chatbot(label="Conversation", height=520)
            with gr.Tabs():
                with gr.TabItem("Chat"):
                    txt = gr.Textbox(placeholder="Type your message here and press Enter...", show_label=False)
                with gr.TabItem("Voice"):
                    mic = gr.Audio(sources=["microphone"], type="numpy", label="Press to speak, release to send")

    demo.load(fn=refresh_sidebar, inputs=None, outputs=[sidebar_items, sidebar_cart])

    refresh_btn.click(fn=refresh_sidebar, inputs=None, outputs=[sidebar_items, sidebar_cart])
    txt.submit(fn=send_text_chat, inputs=[chat, txt], outputs=[chat, sidebar_cart]).then(lambda: "", None, txt)
    mic.change(fn=send_voice_chat, inputs=[chat, mic], outputs=[chat, sidebar_cart])


if __name__ == "__main__":
    demo.launch()

