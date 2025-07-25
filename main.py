from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# 環境変数読み込み
load_dotenv()

app = FastAPI()

# CORS設定（フロントからの直接アクセス許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番ではフロントURLを指定
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAIクライアント
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 受け取りデータ用モデル
class BookRequest(BaseModel):
    title: str
    reading: str
    author: str

@app.post("/api/books")
async def get_similar_books(book: BookRequest):
    # ChatGPTに質問
    prompt = f"""
    次の本と類似する書籍を3冊リストアップしてください。

    タイトル: {book.title}
    読み仮名: {book.reading}
    著者: {book.author}

    以下のJSON形式で出力してください:
    {{
      "similar_books": [
        {{"title": "", "author": ""}},
        {{"title": "", "author": ""}},
        {{"title": "", "author": ""}}
      ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # または gpt-4o
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # ChatGPTの返答を返す
    return response.choices[0].message.content

