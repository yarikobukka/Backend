from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- CORS 設定 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yariko-biblioradar.com",
        "https://api.yariko-biblioradar.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Qdrant
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION = "books"

def embed(text: str):
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return resp.data[0].embedding


class BookRequest(BaseModel):
    title: str
    author: str | None = None


# ★ GET /api/books（動作確認用）
@app.get("/api/books")
async def get_books():
    return {"status": "ok"}

# ★ HEAD /api/books（Cloudflare が使う）
@app.head("/api/books")
async def head_books():
    return {}


# ★ POST /api/books（推薦API）
@app.post("/api/books")
async def recommend_books(req: BookRequest):
    title_vec = embed(req.title)

    title_hits: list[ScoredPoint] = qdrant.search(
        collection_name=COLLECTION,
        query=title_vec,
        limit=5,
    )

    if not title_hits or title_hits[0].score < 0.35:
        return JSONResponse(
            status_code=404,
            content={
                "message": "入力された本がデータベースにありませんでした。",
                "books": [],
            },
        )

    identified_book = title_hits[0].payload

    summary = identified_book.get("summary")
    if not summary:
        return JSONResponse(
            status_code=200,
            content={
                "message": "この本にはサマリーが登録されていないため、類似書籍を推薦できません。",
                "books": [],
            },
        )

    summary_vec = embed(summary)

    similar_hits: list[ScoredPoint] = qdrant.search(
        collection_name=COLLECTION,
        query=summary_vec,
        limit=50,
    )

    seen = set()
    recommended = []
    self_isbn = identified_book.get("isbn")

    for hit in similar_hits:
        payload = hit.payload
        isbn = payload.get("isbn")

        if isbn == self_isbn:
            continue

        if isbn not in seen:
            seen.add(isbn)
            recommended.append(payload)

    return JSONResponse(
        {
            "identified_book": identified_book,
            "books": recommended[:10],
        }
    )
