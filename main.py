from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from generate_keywords import generate_keywords
from ndl_search import search_ndl_books  # ← 上記の改善版を使用
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web-one-beta-11.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookRequest(BaseModel):
    title: str
    author: str

@app.post("/api/books")
async def get_similar_books(book: BookRequest):
    print(f"[INFO] 受信: タイトル='{book.title}', 著者='{book.author}'")

    try:
        keywords = generate_keywords(book.title, book.author)
        print("[INFO] 生成されたキーワード:", keywords)
    except Exception as e:
        print("[ERROR] キーワード生成エラー:", e)
        return JSONResponse(content={"error": "キーワード生成に失敗しました"}, status_code=500)

    if not keywords:
        return JSONResponse(content={"error": "キーワードが生成されませんでした"}, status_code=500)

    keyword_books = {}
    seen_keys = set()

    for keyword in keywords:
        try:
            results = search_ndl_books(keyword, count=100)  # ← 件数を増やして選択肢を広げる
            print(f"[INFO] キーワード '{keyword}' の検索結果:", results)
        except Exception as e:
            print(f"[ERROR] キーワード '{keyword}' の検索中にエラー:", e)
            continue

        if results:
            random.shuffle(results)  # ← 結果をシャッフルして偏りを減らす
            for book_info in results:
                key = (str(book_info.get("title", "")).strip().lower(), str(book_info.get("author", "")).strip().lower())
                if key not in seen_keys:
                    keyword_books[keyword] = book_info
                    seen_keys.add(key)
                    break  # 1件だけ選ぶ

    if not keyword_books:
        return JSONResponse(content={
            "keywords": keywords,
            "books": [],
            "message": "関連書籍が見つかりませんでした。"
        }, status_code=200)

    return JSONResponse(content={
        "keywords": keywords,
        "books": list(keyword_books.values())
    }, status_code=200)