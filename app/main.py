from fastapi import FastAPI
from .routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Voice Shopping Assistant",
    description="Text-based shopping assistant using LangChain + ChromaDB",
    version="0.1.0"
)


app.include_router(router)

@app.get("/")
def root():
    return {"message": "Shopping Assistant API is running"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
