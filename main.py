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

# --- CORS 設定（本番用） ---
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

# Qdrant（HTTP モード）
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION = "books"

# 埋め込み生成
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


# ★ POST /api/books（推薦API）
@app.post("/api/books")
async def recommend_books(req: BookRequest):
    # ① タイトルをベクトル化
    title_vec = embed(req.title)

    # ② タイトル類似検索（最新版 API）
    title_hits: list[ScoredPoint] = qdrant.search(
        collection_name=COLLECTION,
        query_vector=("title_vector", title_vec),
        limit=5,
    )

    # 類似度が低い → DBに存在しないとみなす
    if not title_hits or title_hits[0].score < 0.35:
        return JSONResponse(
            status_code=404,
            content={
                "message": "入力された本がデータベースにありませんでした。",
                "books": [],
            },
        )

    # ③ 最も類似度の高い1冊を「入力された本」とみなす
    identified_book = title_hits[0].payload

    # summary がない本だった場合は推薦できない
    summary = identified_book.get("summary")
    if not summary:
        return JSONResponse(
            status_code=200,
            content={
                "message": "この本にはサマリーが登録されていないため、類似書籍を推薦できません。",
                "books": [],
            },
        )

    # ④ summary をベクトル化
    summary_vec = embed(summary)

    # ⑤ summary_vector を使って類似書籍検索（最新版 API）
    similar_hits: list[ScoredPoint] = qdrant.search(
        collection_name=COLLECTION,
        query_vector=("summary_vector", summary_vec),
        limit=50,
    )

    # ⑥ 重複排除（ISBN）＋ 自分自身は除外
    seen = set()
    recommended = []
    self_isbn = identified_book.get("isbn")

    for hit in similar_hits:
        payload = hit.payload
        isbn = payload.get("isbn")

        # 自分自身は除外
        if isbn == self_isbn:
            continue

        if isbn not in seen:
            seen.add(isbn)
            recommended.append(payload)

    # ⑦ 上位10件返す
    return JSONResponse(
        {
            "identified_book": identified_book,
            "books": recommended[:10],
        }
    )
