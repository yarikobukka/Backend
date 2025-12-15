from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from generate_keywords import generate_keywords
from ndl_search import search_ndl_books
import random

app = FastAPI(
    docs_url=None,

    redoc_url=None,

    openapi_url=None

)

# CORS設定：フロントエンドからのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web-one-beta-11.vercel.app",
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストボディの定義
class BookRequest(BaseModel):
    title: str
    author: str

# 書籍推薦APIエンドポイント
@app.post("/api/books")
async def get_similar_books(book: BookRequest):
    print(f"[INFO] 受信: タイトル='{book.title}', 著者='{book.author}'")

    # キーワード生成（OpenAI）
    keywords = generate_keywords(book.title, book.author)
    print("[INFO] 生成されたキーワード:", keywords)

    if not keywords:
        return JSONResponse(content={"error": "キーワード生成に失敗しました"}, status_code=500)

    keyword_books = {}

    for keyword in keywords:
        # NDL検索：上位10件を取得
        results = search_ndl_books(keyword, count=10)
        print(f"[INFO] キーワード '{keyword}' の検索結果:", results)

        if results:
            # ランダムに1冊選択
            book_info = random.choice(results)

            # 重複チェック（タイトル＋著者の組み合わせ）
            key = (str(book_info["title"]).strip().lower(), str(book_info["author"]).strip().lower())
            if key not in [(str(b["title"]).strip().lower(), str(b["author"]).strip().lower()) for b in keyword_books.values()]:
                keyword_books[keyword] = book_info

    # 書籍が見つからなかった場合
    if not keyword_books:
        return JSONResponse(content={
            "keywords": keywords,
            "books": [],
            "message": "関連書籍が見つかりませんでした。"
        }, status_code=200)

    # 書籍とキーワードを返す（正常系）
    return JSONResponse(content={
        "keywords": keywords,
        "books": list(keyword_books.values())  # ← リスト形式で返すとフロントで扱いやすい
    }, status_code=200)

# APIエンドポイント定義を全部書いたあとに
app.mount("/", StaticFiles(directory="/home/akiko/Book", html=True), name="static")