import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_keywords(title: str, author: str) -> list[str]:
    prompt = f"""
次の本に関連するテーマやジャンルを3つ、検索キーワードとして抽出してください。
タイトル: {title}
著者: {author}

形式:
["キーワード1", "キーワード2", "キーワード3"]
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは検索キーワードを抽出するアシスタントです。"},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    try:
        keywords = eval(content)  # JSONではなくPythonリスト形式で返ってくることが多い
        if isinstance(keywords, list):
            return keywords
    except Exception:
        pass
    return []
