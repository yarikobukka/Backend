from flask import Flask, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 読み込み
load_dotenv()

# Flask アプリ作成
app = Flask(__name__)

# OpenAI クライアント
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ルートエンドポイント
@app.route("/")
def read_root():
    response = client.chat.completions.create(
        model="gpt-4o",  # 正しいモデル名を指定
        messages=[
            {
                "role": "user",
                "content": "東方プロジェクトの古明地さとりについて教えて"
            }
        ]
    )
    return jsonify({"story": response.choices[0].message.content})

# Vercel は app オブジェクトを自動検知する



