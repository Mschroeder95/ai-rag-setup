from fastapi import FastAPI
from routes import chat, embed

app = FastAPI(title="AI RAG")
app.include_router(chat.router)
app.include_router(embed.router)