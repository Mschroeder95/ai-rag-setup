from typing import Any

from ollama import Message
from . import chroma_client
import json
from util import safe_string
from routes.embed import post_embed_single, EmbedRequest
import json


def get_chroma_document_by_id(id: str, collection_name: str) -> Any:
    coll = chroma_client.get_collection(name=safe_string(collection_name))
    data = coll.get(ids=[safe_string(id)])
    return json.loads(data["documents"][0])


async def update_chat_history(
    collection_name: str, chat_id: str, chat_history: list[Message]
):
    await post_embed_single(
        EmbedRequest(
            id=chat_id,
            collection_name=collection_name,
            text=json.dumps({"chat_history": chat_history}),
        )
    )


def get_chat_history(collection_name: str, chat_id: str) -> list[Message]:
    coll = chroma_client.get_collection(name=safe_string(collection_name))
    response = coll.get(ids=[f"{safe_string(chat_id)}"])
    if not response['documents']:
        return []
    chat_history = json.loads(response["documents"][0])
    return chat_history["chat_history"]
