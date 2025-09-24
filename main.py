from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

# 環境変数読み込み
load_dotenv()

# FastAPIインスタンス作成
app = FastAPI()

# CORS設定（フロントからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のURLに制限
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAIクライアント設定
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 受け取るリクエストの形式
class BookRequest(BaseModel):
    title: str
    reading: str
    author: str

@app.post("/api/books")
async def get_similar_books(book: BookRequest):
    prompt = f"""
    次の本と類似する書籍を3冊、以下のJSON形式で出力してください。説明や前置きは不要です。JSONのみを返してください。

    タイトル: {book.title}
    読み仮名: {book.reading}
    著者: {book.author}

    形式:
    {{
      "similar_books": [
        {{"title": "", "author": ""}},
        {{"title": "", "author": ""}},
        {{"title": "", "author": ""}}
      ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content
    import re
    # JSON部分だけ抽出する例（簡易的）
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            result_json = json.loads(match.group())
            return JSONResponse(content=result_json)      
        except json.JSONDecodeError:
            return JSONResponse(content={"error": "JSON parse failed", "raw": content}, status_code=500)
@app.options("/api/books")
async def options_books():
    return JSONResponse(content={}, status_code=200)