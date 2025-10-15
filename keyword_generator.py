import os
import ast
from dotenv import load_dotenv
from openai import OpenAI
from typing import List

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_keywords(title: str, author: str) -> List[str]:
    prompt = f"""
次の本に関連するテーマやジャンルを3つ、検索キーワードとして抽出してください。
タイトル: {title}
著者: {author}

形式:
["キーワード1", "キーワード2", "キーワード3"]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは書籍のキーワードを生成するアシスタントです"},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content.strip()
        keywords = ast.literal_eval(content)
        if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
            return keywords
    except Exception as e:
        print(f"[ERROR] キーワード生成失敗: {e}")

    return []
