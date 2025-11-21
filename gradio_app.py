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
    lines = ["<strong style='font-size:1.05rem;'>Categories</strong>"]
    for cat in categories:
        lines.append(
            f"<details><summary style='cursor:pointer; font-weight:700; color:#0f172a; background:#fef3c7; padding:6px 10px; border-radius:10px; display:inline-block;'>{cat['category'].title()}</summary>"
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


CUSTOM_CSS = """
.gradio-container {
    max-width: 100% !important;
    width: 100vw;
    min-height: 100vh;
    min-width: 100vw;
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: linear-gradient(180deg, #f4f7fb 0%, #e8edf5 40%, #ffffff 100%);
    padding: 30px 40px 50px 40px;
    box-sizing: border-box;
}
#root,
body {
    margin: 0;
    width: 100vw;
    min-height: 100vh;
    background: #0f172a;
}
.gr-blocks {
    width: 100%;
}

#hero-card {
    background: #0f172a;
    border-radius: 22px;
    padding: 28px;
    color: #e2e8f0;
    box-shadow: 0 25px 65px rgba(15, 23, 42, 0.35);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
}
#hero-card h1 {
    font-size: 2.5rem;
    margin-bottom: 0.6rem;
    color: #f8fafc;
}
#hero-card p {
    color: #cbd5f5;
    margin: 0.2rem 0;
}
#hero-card img {
    max-height: 110px;
    filter: drop-shadow(0 15px 35px rgba(0,0,0,0.35));
}
#items_md, #cart_md {
    background: linear-gradient(135deg, #ffffff, #f1f5f9);
    border-radius: 18px;
    padding: 18px 22px;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
    color: #0f172a;
    border: 1px solid #e2e8f0;
}
#items_md *, #cart_md * {
    color: #0f172a !important;
}
#items_md details summary {
    list-style: none;
    color: #0f172a;
    font-weight: 600;
}
#items_md details {
    padding: 6px 0;
}
#items_md li {
    margin-bottom: 6px;
    color: #1e293b;
}
#items_md strong {
    color: #0f172a;
}
#cart_md {
    margin-top: 18px;
}
#cart_md strong {
    color: #f97316;
}
#cart_md strong {
    color: #f97316 !important;
}
#cart_md p, #cart_md li {
    color: #1e293b !important;
}
.gr-chatbot {
    border-radius: 30px !important;
    box-shadow: 0 30px 70px rgba(15, 23, 42, 0.2);
    min-height: 560px;
    background: #ffffff;
}
.tab-nav button {
    font-weight: 600;
    color: #475569;
    opacity: 1;
}
.tab-nav button:hover {
    color: #f97316;
}
.tab-nav button.selected {
    color: #f97316;
    border-bottom: 3px solid #f97316;
    opacity: 1;
}
.section-heading {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: 0.04em;
    margin-bottom: 10px;
    padding-left: 6px;
}
footer,
button[aria-label="Settings"],
button[aria-label="settings"],
#share-btn,
.share-btn {
    display: none !important;
}
"""

with gr.Blocks(title="Shopping Assistant", css=CUSTOM_CSS, theme=gr.themes.Soft(primary_hue="orange", neutral_hue="slate")) as demo:
    gr.Markdown(
        """
        <div id="hero-card">
            <div>
                <p style="letter-spacing:4px; text-transform:uppercase; font-size:0.8rem; color:#fbbf24;">Personal AI Shopper</p>
                <h1>🛒 Voice Shopping Assistant</h1>
                <p>Discover categories, compare prices instantly, and keep your cart updated like a modern e-commerce storefront.</p>
            </div>
            <img src="https://cdn-icons-png.flaticon.com/512/891/891419.png" alt="Shopping illustration" />
        </div>
        """,
        elem_id="hero"
    )
    with gr.Row():
        with gr.Column(scale=1, min_width=320):
            gr.Markdown(
                "<div class='section-heading'>🗂️ Browse Items</div>",
                elem_id="browse-heading"
            )
            sidebar_items = gr.Markdown(value="Loading items...", elem_id="items_md")
            gr.Markdown(
                "<div class='section-heading'>🛒 Cart Overview</div>",
                elem_id="cart-heading"
            )
            sidebar_cart = gr.Markdown(value="Loading cart...", elem_id="cart_md")
            with gr.Row():
                refresh_btn = gr.Button("Refresh Inventory ✨", variant="secondary")
        with gr.Column(scale=3):
            chat = gr.Chatbot(label="Conversation", height=520, bubble_full_width=False)
            with gr.Tabs(elem_classes=["tab-nav"]):
                with gr.TabItem("💬 Chat"):
                    txt = gr.Textbox(placeholder="Type your message here and press Enter...", show_label=False)
                with gr.TabItem("🎙️ Voice"):
                    mic = gr.Audio(sources=["microphone"], type="numpy", label="Press to speak, release to send")

    demo.load(fn=refresh_sidebar, inputs=None, outputs=[sidebar_items, sidebar_cart])

    refresh_btn.click(fn=refresh_sidebar, inputs=None, outputs=[sidebar_items, sidebar_cart])
    txt.submit(fn=send_text_chat, inputs=[chat, txt], outputs=[chat, sidebar_cart]).then(lambda: "", None, txt)
    mic.change(fn=send_voice_chat, inputs=[chat, mic], outputs=[chat, sidebar_cart])


if __name__ == "__main__":
    demo.launch()

