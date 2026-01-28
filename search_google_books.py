# search_google_books.py

# 1〜2行目：dotenv と os を読み込む
from dotenv import load_dotenv
import os

# 4行目：.env を読み込む
load_dotenv()

# 6行目：APIキーを環境変数から取得
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

# 8行目以降：必要なライブラリ
import requests
import time

# ここから関数本体
def search_google_books(keyword: str, count: int = 10):
    url = "https://www.googleapis.com/books/v1/volumes"

    params = {
        "q": keyword,
        "maxResults": 40,
        "printType": "books",
        "langRestrict": "ja",
        "key": API_KEY   # ← ここで使われる
    }

    time.sleep(1)  # 429回避

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print("[ERROR] Google Books API リクエスト失敗:", e)
        return []

    data = response.json()
    if "items" not in data:
        return []

    books = []
    for item in data["items"]:
        info = item.get("volumeInfo", {})
        title = info.get("title", "タイトル不明")
        authors = info.get("authors", ["著者不明"])

        books.append({
            "title": title,
            "author": ", ".join(authors)
        })

    return books
if __name__ == "__main__":
    print("API_KEY:", API_KEY)