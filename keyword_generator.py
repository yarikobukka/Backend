from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_keywords(title: str, author: str) -> list[str]:
    prompt = f"""
次の本に関連するテーマやジャンルを3つ、検索キーワードとして抽出してください。
タイトル: {title}
著者: {author}

形式:
["キーワード1", "キーワード2", "キーワード3"]
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは書籍のキーワードを生成するアシスタントです"},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        keywords = eval(content)  # 例: ["文学", "猫", "明治時代"]
        if isinstance(keywords, list):
            return keywords
    except Exception:
        pass

    return []
