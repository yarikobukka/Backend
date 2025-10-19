import os
import ast
from dotenv import load_dotenv
from openai import OpenAI
from typing import List

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_keywords(title: str, author: str) -> List[str]:
    prompt = f"""
次の本に関連するテーマやジャンルを3つ、日本語の検索キーワードとして抽出してください。
できるだけ異なる語頭の言葉を選び、ジャンルや内容に幅を持たせてください。
タイトル: {title}
著者: {author}

形式（JSON）:
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
        print("[DEBUG] OpenAI応答:", content)

        try:
            keywords = ast.literal_eval(content)
        except Exception:
            keywords = [k.strip() for k in content.split(",") if k.strip()]

        if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
            return keywords

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] キーワード生成失敗: {e}")

    return []