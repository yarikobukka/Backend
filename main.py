from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from generate_keywords import generate_keywords
from ndl_search import search_ndl_books

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

    keywords = generate_keywords(book.title, book.author)
    print("[INFO] 生成されたキーワード:", keywords)

    if not keywords:
        return JSONResponse(content={"error": "キーワード生成に失敗しました"}, status_code=500)

    keyword_books = {}
    for keyword in keywords:
        results = search_ndl_books(keyword, count=1)
        print(f"[INFO] キーワード '{keyword}' の検索結果:", results)
        if results:
            book_info = results[0]
            key = (str(book_info["title"]).strip().lower(), str(book_info["author"]).strip().lower())
            if key not in keyword_books.values():
                keyword_books[keyword] = book_info

    if not keyword_books:
        return JSONResponse(content={
            "keywords": keywords,
            "books": [],
            "message": "関連書籍が見つかりませんでした。"
        }, status_code=200)

    return JSONResponse(content={
        "keywords": keywords,
        "books": keyword_books
    })