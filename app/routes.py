from fastapi import APIRouter, Body, UploadFile, File, HTTPException
from app.products import get_all_products, find_product_by_name
from app.cart import get_cart
from app.chatbot import process_user_message
from app.models import ChatRequest, ChatResponse
from app.audio_service import get_audio_service
import tempfile
import os

router = APIRouter()

@router.get("/items")
def items():
    """Return all available products grouped by category."""
    return get_all_products()

@router.get("/items_dropdown")
def items_dropdown():
    """Return items in dropdown-friendly grouping.
    {"categories": [{"category": str, "items": [{name, price, unit}]}]}
    """
    data = get_all_products()
    categories = []
    for category, items in data.items():
        categories.append({
            "category": category,
            "items": [{"name": i.get("name"), "price": i.get("price"), "unit": i.get("unit")} for i in items]
        })
    return {"categories": categories}

def _cart_summary():
    items = get_cart()  
    counts = {}
    for it in items:
        name = (it.get("name") or "").strip()
        if not name:
            continue
        counts[name] = counts.get(name, 0) + 1

    summary_items = []
    total = 0.0
    for name, qty in counts.items():
        product = find_product_by_name(name)
        price = float(product.get("price", 0)) if product else 0.0
        unit = product.get("unit") if product else ""
        subtotal = price * qty
        total += subtotal
        summary_items.append({
            "name": name,
            "unit": unit,
            "price": price,
            "quantity": qty,
            "subtotal": subtotal,
        })

    return {"items": summary_items, "total": total}

@router.get("/cart")
def cart():
    """Return current cart contents with quantities, price and totals."""
    return _cart_summary()

@router.post("/chat")
def chat(body: dict = Body(...)):
    """
    Process a user message via LangChain + Chroma pipeline.
    Accepts either {"message": str} or {"text": str}
    """
    message = body.get("message") or body.get("text") or ""
    result = process_user_message(message)
  
    result["cart"] = _cart_summary()
    return result

@router.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe audio file to text using Faster-Whisper.
    Accepts audio files in common formats (wav, mp3, m4a, etc.)
    """
    try:
       
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
    
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1]}") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
           
            audio_service = get_audio_service()
            transcribed_text = audio_service.transcribe_audio_file(temp_file_path)
            
            if transcribed_text is None:
                raise HTTPException(status_code=400, detail="Could not transcribe audio. Please ensure the audio contains clear speech.")
            
            return {
                "transcribed_text": transcribed_text,
                "success": True
            }
            
        finally:
            
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/voice-chat")
async def voice_chat(audio_file: UploadFile = File(...)):
    """
    Complete voice-to-chat pipeline: transcribe audio and process as chat message.
    Returns both transcription and chatbot response.
    """
    try:
       
        transcription_result = await transcribe_audio(audio_file)
        transcribed_text = transcription_result["transcribed_text"]
        
       
        chat_result = process_user_message(transcribed_text)
        chat_result["cart"] = _cart_summary()
        
      
        return {
            "transcribed_text": transcribed_text,
            "chat_response": chat_result,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice chat processing failed: {str(e)}")
