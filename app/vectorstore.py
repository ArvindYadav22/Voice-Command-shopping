from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import json
from pathlib import Path
from .config import OPENAI_API_KEY

PROJECT_ROOT = Path(__file__).parent.parent
PRODUCTS_FILE = PROJECT_ROOT / "products.json"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

def init_vectorstore():
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectorstore = Chroma(
        collection_name="products",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )

    
    try:
        count = vectorstore._collection.count() 
    except Exception:
        count = 0

    if count == 0:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            products = json.load(f)

        texts, metadatas = [], []
        for category, items in products.items():
            for item in items:
                unit = item.get("unit", "N/A")
                price = item.get("price", "N/A")
                text = f"{item['name']} - {unit} - Rs.{price} - Category: {category}"
                texts.append(text)
                metadatas.append({"category": category, **item})

        if texts:
            vectorstore.add_texts(texts=texts, metadatas=metadatas)

    return vectorstore
