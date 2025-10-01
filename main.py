from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from keyword_generator import generate_keywords
from ndl_search import search_ndl_books

app = FastAPI()

class BookRequest(BaseModel):
    title: str
    author: str

@app.post("/api/books")
async def get_similar_books(book: BookRequest):
    # ステップ①：ChatGPTで検索キーワードを生成
    keywords = generate_keywords(book.title, book.author)
    if not keywords:
        return JSONResponse(content={"error": "キーワード生成に失敗しました"}, status_code=500)

    # ステップ②：NDL APIで類似書籍を検索
    ndl_books = []
    for keyword in keywords:
        results = search_ndl_books(keyword)
        ndl_books.extend(results)

    # 重複を除去（タイトル＋著者でユニーク化）
    seen = set()
    unique_books = []
    for b in ndl_books:
        key = (str(b["title"]), str(b["author"]))
        if key not in seen:
            seen.add(key)
            unique_books.append(b)

    if not unique_books:
        return JSONResponse(content={"message": "類似書籍が見つかりませんでした"}, status_code=404)

    # ステップ③：推薦文は不要なので省略

    return JSONResponse(content={
        "keywords": keywords,
        "books": unique_books
    })