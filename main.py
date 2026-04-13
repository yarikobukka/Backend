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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://web-one-beta-11.vercel.app",
        "https://yariko-biblioradar.com",
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
    prefer_grpc=False,
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


@app.post("/api/books")
async def recommend_books(req: BookRequest):
    # ① タイトルをベクトル化
    title_vec = embed(req.title)

    # ② タイトル類似検索（入力された本を特定するため）
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

    # ③ もっとも類似度の高い1冊を「入力された本」とみなす
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

    # ④ その本の summary をベクトル化
    summary_vec = embed(summary)

    # ⑤ summary_vector を使って類似書籍検索
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

    # ⑦ 上位10件返す（必要ならスコアでフィルタも可）
    return JSONResponse(
        {
            "identified_book": identified_book,  # 特定した元の本（必要なければ削除してOK）
            "books": recommended[:10],
        }
    )