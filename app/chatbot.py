import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .vectorstore import init_vectorstore
from .cart import add_to_cart, remove_from_cart, clear_cart
from .config import OPENAI_API_KEY
from .products import find_product_by_name

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=OPENAI_API_KEY
)
vectorstore = init_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_template(
    """
You are a witty, persuasive shopping assistant who can also answer general questions.
Always be helpful, concise, and charming; when relevant, nudge toward a purchase with tasteful upsell/cross-sell suggestions.

User query: {query}
Relevant products (may be empty): {context}
Valid items you are allowed to reference for cart actions: {valid_items}
Conversation history (last 5 messages):
{history}

Tasks:
1) Determine action among [add, remove, show, clear, none]. Use 'clear' when the user wants to remove all items from the cart. Use 'none' if no cart action is appropriate.
2) Decide item name for add/remove if confidently identified; else empty string.
3) Compose a short salesperson-style reply that either answers the question or moves the user toward a purchase.

Return ONLY valid JSON:
{{"action":"<add|remove|show|clear|none>","item":"<item name or empty>","reply":"<witty helpful response>"}}

Rules:
- If you choose add/remove, the item MUST be exactly one from the Valid items list above. Otherwise set action to 'none'.
- For general questions or unavailable items, prefer 'none' and provide a helpful reply with suggestions.
"""
)

parser = JsonOutputParser()

conversation_history = []  

def _build_history_block():
    if not conversation_history:
        return ""
    lines = []
    for role, content in conversation_history[-5:]:
        lines.append(f"{role}: {content}")
    return "\n".join(lines)

def process_user_message(message: str):
   
    docs = retriever.invoke(message)
    context = "\n".join([getattr(d, "page_content", str(d)) for d in docs])
    candidate_names = []
    for d in docs:
        try:
            name = (d.metadata.get("name") or "").strip()
        except Exception:
            name = ""
        if name:
            candidate_names.append(name)
    unique_names = []
    seen = set()
    for n in candidate_names:
        key = n.lower()
        if key not in seen:
            seen.add(key)
            unique_names.append(n)
    valid_items_str = ", ".join(unique_names) if unique_names else ""

    history_block = _build_history_block()
    chain_input = {"query": message, "context": context, "valid_items": valid_items_str, "history": history_block}
    response = llm.invoke(prompt.format(**chain_input))

    try:
        data = parser.parse(response.content)
    except Exception:
        try:
            data = json.loads(response.content)
        except Exception:
            return {"reply": "Sorry, I couldn't understand that."}

    action = (data.get("action") or "").strip().lower()
    item_name = (data.get("item") or "").strip()
    reply_text = (data.get("reply") or "").strip()

    if action == "add" and item_name:
        if find_product_by_name(item_name):
            add_to_cart({"name": item_name})
            assistant_reply = reply_text or f"Added {item_name} to your cart."
            conversation_history.append(("user", message))
            conversation_history.append(("assistant", assistant_reply))
            return {"reply": assistant_reply}
        suggestions = ", ".join(unique_names[:3]) if unique_names else ""
        suggest_line = f" Did you mean: {suggestions}?" if suggestions else ""
        assistant_reply = f"I couldn't find '{item_name}' in our catalog.{suggest_line}"
        conversation_history.append(("user", message))
        conversation_history.append(("assistant", assistant_reply))
        return {"reply": assistant_reply}
    if action == "remove" and item_name:
        if find_product_by_name(item_name):
            removed = remove_from_cart(item_name)
            if removed:
                assistant_reply = reply_text or f"Removed {item_name} from your cart."
            else:
                assistant_reply = f"{item_name} was not in your cart."
            conversation_history.append(("user", message))
            conversation_history.append(("assistant", assistant_reply))
            return {"reply": assistant_reply}
        suggestions = ", ".join(unique_names[:3]) if unique_names else ""
        suggest_line = f" Available now: {suggestions}." if suggestions else ""
        assistant_reply = f"'{item_name}' isn't in the current catalog.{suggest_line}"
        conversation_history.append(("user", message))
        conversation_history.append(("assistant", assistant_reply))
        return {"reply": assistant_reply}
    if action == "show":
        assistant_reply = reply_text or "Here is your cart."
        conversation_history.append(("user", message))
        conversation_history.append(("assistant", assistant_reply))
        return {"reply": assistant_reply}
    if action == "clear":
        clear_cart()
        assistant_reply = reply_text or "Cleared your cart."
        conversation_history.append(("user", message))
        conversation_history.append(("assistant", assistant_reply))
        return {"reply": assistant_reply}
    
    assistant_reply = reply_text or "Happy to help!"
    conversation_history.append(("user", message))
    conversation_history.append(("assistant", assistant_reply))
    return {"reply": assistant_reply}
