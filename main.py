from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from generate_keywords import generate_keywords
from ndl_search import search_ndl_books

app = FastAPI()

# CORS設定（ドメイン単位で許可）
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

    keywords = generate_keywords(book.title, book.author)
    print("[INFO] 生成されたキーワード:", keywords)

    if not keywords:
        return JSONResponse(content={"error": "キーワード生成に失敗しました"}, status_code=500)

    ndl_books = []
    for keyword in keywords:
        results = search_ndl_books(keyword)
        print(f"[INFO] キーワード '{keyword}' の検索結果:", results)
        ndl_books.extend(results)

    # 重複除去（タイトル＋著者を正規化して比較）
    seen = set()
    unique_books = []
    for b in ndl_books:
        key = (str(b["title"]).strip().lower(), str(b["author"]).strip().lower())
        if key not in seen:
            seen.add(key)
            unique_books.append(b)

    print("[INFO] ユニークな書籍数:", len(unique_books))

    if not unique_books:
        return JSONResponse(content={
            "keywords": keywords,
            "books": [],
            "message": "関連書籍が見つかりませんでした。キーワードや検索条件を調整して再度お試しください。"
        }, status_code=200)

    return JSONResponse(content={
        "keywords": keywords,
        "books": unique_books
    })