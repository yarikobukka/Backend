import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def format_with_chatgpt(book_list: list[dict]) -> str:
    prompt = f"""
以下の書籍リストを、読者におすすめする形で簡潔に紹介してください。
説明は短く、親しみやすいトーンでお願いします。

{json.dumps(book_list, ensure_ascii=False)}
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは親しみやすい書籍紹介アシスタントです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content