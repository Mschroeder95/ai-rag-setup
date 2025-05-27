# 🧠 AI RAG Setup

**A private, Dockerized Retrieval-Augmented Generation (RAG) backend with document upload and contextual chat capabilities.**  
This project provides a powerful FastAPI-based backend for securely chatting with an AI assistant that understands your custom documents.

---

## 🚀 Features

- 📄 **PDF Document Upload**  
  Upload and embed PDF files for contextual AI interactions.

- 💬 **Chat Interface**  
  Engage in natural language conversation, with responses grounded in your uploaded documents.

- 🧠 **RAG Architecture**  
  Combines large language models with document context retrieval using `Ollama` and `ChromaDB`.

---

## ⚙️ Getting Started

### 🔧 Build and Start the Project

```powershell
docker-compose up --build -d
docker-compose exec ollama sh -c 'ollama_ai_rag pull $OLLAMA_MODEL && ollama_ai_rag pull $OLLAMA_EMBED_MODEL'
```

Ensure your `.env` file includes the model names:

```env
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

## 🧼 Resetting with a New Model (⚠️ Will Delete Data)

If you want to switch to a different model or clean the database:

```powershell
# WARNING: This removes all volume data
docker compose down
docker compose down -v
```

Restart your terminal session and run:

```powershell
docker-compose up -d --force-recreate
docker-compose exec ollama sh -c 'ollama_ai_rag pull $OLLAMA_MODEL && ollama_ai_rag pull $OLLAMA_EMBED_MODEL'
```

Make sure the new embedding model is compatible!

---

## 📥 API Endpoints
The API is fully documented using FastAPI’s interactive Swagger UI.

🔗 Visit [http://localhost:8000/docs](http://localhost:8000/docs) after starting the containers to explore and test the endpoints directly in your browser.

### `/chat` – Chat with Document Context

- Accepts: `collection_name`, `chat_id?`, `words`
- Returns: Assistant response + updated chat history

### `/embed-pdf` – Upload & Embed PDFs

- Accepts: `file`, `collection_name`, optional `metadata`
- Splits and embeds PDF content into your vector DB.

### `/embed-single` – Embed Custom Text

- Accepts: `text`, `collection_name`, optional `id`, optional `metadata`
- Directly inserts single document entries into the vector store.

---

## 🗂 Tech Stack

- **FastAPI** – Web framework for API routes  
- **ChromaDB** – Vector store for document embeddings  
- **Ollama** – Lightweight LLM runtime and embedding generator  
- **LangChain** – PDF parsing and chunking  
- **Docker Compose** – Container orchestration for easy deployment

---

## 📎 Example Workflow

1. 🧾 Upload a PDF to `/embed-pdf`
2. 🧠 Ask a question at `/chat` referencing the uploaded collection
3. 💬 Get contextual responses based on your document content

---

## 🛡️ Notes

- Ensure documents are properly formatted and readable before upload.
- Metadata allows for future filtering and contextual refinement.

---

## 📣 Contributions

Feel free to fork and extend this repo. PRs and suggestions are welcome!