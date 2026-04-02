from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS（必要なら残す）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://web-one-beta-11.vercel.app"
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
    prefer_grpc=False
)

COLLECTION = "books"

# 埋め込み生成
def embed(text: str):
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding

# リクエスト形式
class BookRequest(BaseModel):
    title: str
    author: str | None = None


# -------------------------
# 📘 推薦API（Qdrant）
# -------------------------
@app.post("/api/books")
async def recommend_books(req: BookRequest):

    # ① タイトルをベクトル化
    query_vec = embed(req.title)

    # ② タイトル類似検索
    title_hits: list[ScoredPoint] = qdrant.search(
        collection_name=COLLECTION,
        query_vector=("title_vector", query_vec),
        limit=50
    )

    # --- A仕様：類似度が低い＝DBに存在しない ---
    if not title_hits or title_hits[0].score < 0.35:
        return JSONResponse(
            status_code=404,
            content={
                "message": "入力された本がデータベースにありませんでした。",
                "books": []
            }
        )
    # ---------------------------------------------

    # ③ summary がある本だけ対象
    valid_hits = [h for h in title_hits if h.payload.get("summary")]

    if not valid_hits:
        return JSONResponse({"books": []})

    # ④ summary の埋め込みを一括生成
    summaries = [h.payload["summary"] for h in valid_hits]
    summary_vecs = [embed(s) for s in summaries]

    # ⑤ summary_vector で再ランキング
    re_ranked = []
    for vec in summary_vecs:
        result = qdrant.search(
            collection_name=COLLECTION,
            query_vector=("summary_vector", vec),
            limit=1
        )
        if result:
            re_ranked.append(result[0])

    # ⑥ 重複排除（ISBN）
    seen = set()
    unique_books = []
    for hit in re_ranked:
        isbn = hit.payload.get("isbn")
        if isbn not in seen:
            seen.add(isbn)
            unique_books.append(hit.payload)

    # ⑦ 上位10件返す
    return JSONResponse({"books": unique_books[:10]})


# -------------------------
# 🌐 フロントエンド配信
# -------------------------
# ここをあなたのフロントのパスに合わせてね
FRONT_DIR = "/home/akiko/Book"

app.mount("/", StaticFiles(directory=FRONT_DIR, html=True), name="static")