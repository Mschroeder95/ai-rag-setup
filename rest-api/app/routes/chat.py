import json
from fastapi import APIRouter, Form, HTTPException, status
from ollama import ChatResponse
from pydantic import BaseModel
import yaml
from config import OLLAMA_EMBED_MODEL, OLLAMA_MODEL
from clients import ollama_client, chroma_client
from clients.chromadb_helpers import update_chat_history, get_chat_history
from util import safe_string

router = APIRouter()


class ChatRequest(BaseModel):
    collection_name: str = Form(
        ..., description="The name of the collection with desired context"
    )
    chat_id: str = Form(
        None, description="The id for chat history context, if empty, one is created."
    )
    words: str = Form(..., description="The words to say the the assistant")


class ChatResponseFormat(BaseModel):
    assistant_response: str


@router.post(
    "/chat", summary="Chat with an assistant", description="Chat with an assistant"
)
async def post_chat(req: ChatRequest):

    # returns an embedding vector from the users chat input. Needed for searching RAG for similar vectors.
    embedding = ollama_client.embed(model=OLLAMA_EMBED_MODEL, input=req.words)
    
    # Initialize variables
    collection_name = safe_string(req.collection_name)
    chat_id = req.chat_id
    words = req.words

    # Get the collection that was created when the PDF was uploaded
    try:
        coll = chroma_client.get_collection(name=collection_name)
    except ValueError as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chroma add failed: {e}",
        )

    # Query for broad context. Uses the users input and seaches the RAG For similar vectors
    query_result = coll.query(query_embeddings=embedding["embeddings"], n_results=5)
    general_data = query_result["documents"]

    # Retrieve the chat history
    chat_history = get_chat_history(collection_name=collection_name, chat_id=chat_id)
    
    # The users new message
    new_message = {"role": "user", "content": f"{words}"}

    # Initialize prompt to tell the system how to behave
    system_prompt = {
        "role": "system",
        "content": f"""
                You are a helpful assistant.

                Here is relevant document data:
                {yaml.safe_dump(general_data)}
            """
    }

    # Build the chat messages
    full_chat = []
    full_chat.extend(chat_history)
    full_chat.append(new_message)
    full_chat.append(system_prompt)

    # Call Ollama chat
    output: ChatResponse = ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=full_chat,
        format=ChatResponseFormat.model_json_schema(),
        options={
        "num_ctx": 8192,
        "num_predict": 2048,
    },
    )

    # Remove system prompt before saving
    full_chat.pop()  

    # Append the models response to the chat and save
    full_chat.append(output.message.model_dump())
    await update_chat_history(collection_name, chat_id, full_chat)

    # Build the response model
    assistant_response = ChatResponseFormat(**json.loads(output.message.content))
    return {
        "assistant_response": assistant_response.assistant_response,
        "chat_history": full_chat,
    }
