import shutil
from typing import Optional
import uuid
from chromadb import Metadata
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from config import OLLAMA_EMBED_MODEL
from clients import ollama_client, chroma_client
from util import safe_string
from langchain_community.document_loaders import PyPDFLoader


router = APIRouter()


class EmbedResponse(BaseModel):
    collection_name: str
    id: str


class EmbedRequest(BaseModel):
    id: str = Field(None, description="Optional ID for the new embedding")
    collection_name: str = Field(
        ..., description="The collection to embed context into"
    )
    text: str = Field(..., description="The text to embed")
    metadata: Optional[Metadata] = Field(
        None, description="Matadata for future query filtering."
    )


@router.post(
    "/embed-single",
    summary="Embed text into the RAG system",
    description="Low level interface for embedding text into the RAG.",
)
async def post_embed_single(req: EmbedRequest):
    collection_name = safe_string(req.collection_name)
    try:
        resp = ollama_client.embed(model=OLLAMA_EMBED_MODEL, input=req.text)
        embeddings = resp["embeddings"]
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ollama embed failed: {e}"
        )

    try:
        coll = chroma_client.get_collection(name=collection_name)
    except Exception:
        chroma_client.create_collection(name=collection_name)
        coll = chroma_client.get_collection(name=collection_name)

    if req.metadata is not None:
        instert_metadatas = [req.metadata]
    else:
        instert_metadatas = None

    if req.id is not None:
        insert_ids = [safe_string(req.id)]
    else:
        insert_ids = [str(uuid.uuid4())]

    try:
        coll.add(
            ids=insert_ids,
            embeddings=embeddings,
            documents=[req.text],
            metadatas=instert_metadatas,
        )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Chroma add failed: {e}"
        )

    return EmbedResponse(id=insert_ids[0], collection_name=collection_name)


class EmbedPDFRequest(BaseModel):
    file: UploadFile = File(..., description="A PDF file")
    collection_name: str = Form(..., description="The collection to save the data to")
    metadata: Optional[Metadata] = Form(
        None, description="Matadata for future query filtering."
    )


@router.post("/embed-pdf", status_code=status.HTTP_201_CREATED)
async def embed_pdf(req: EmbedPDFRequest = Depends()):
    file = req.file
    collection_name = req.collection_name
    metadata = req.metadata
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Only PDF uploads are supported"
        )

    tmp_path = f"/tmp/{file.filename}"
    try:
        with open(tmp_path, "wb") as out:
            shutil.copyfileobj(file.file, out)

        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        if not docs:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Couldn’t extract any text"
            )
        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
        chunks = splitter.split_documents(docs)
        embed_data = []
        ids = []
        for chunk in chunks:
            ids.append(str(uuid.uuid4()))
            embed_data.append(chunk.page_content)

        ollama_client.embed(OLLAMA_EMBED_MODEL, input=embed_data)

        collection_name = safe_string(collection_name)
        try:
            resp = ollama_client.embed(model=OLLAMA_EMBED_MODEL, input=embed_data)
            embeddings = resp["embeddings"]
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ollama embed failed: {e}",
            )

        try:
            coll = chroma_client.get_collection(name=collection_name)
        except Exception:
            chroma_client.create_collection(name=collection_name)
            coll = chroma_client.get_collection(name=collection_name)

        if metadata is not None:
            instert_metadatas = [metadata]
        else:
            instert_metadatas = None

        try:
            coll.add(
                ids=ids,
                embeddings=embeddings,
                documents=embed_data,
                metadatas=instert_metadatas,
            )
        except Exception as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Chroma add failed: {e}"
            )

        return {"ids": ids, "collection_name": collection_name}

    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))