import requests
import xmltodict
import random

def search_ndl_books(keyword: str, count: int = 100):
    url = "https://ndlsearch.ndl.go.jp/api/opensearch"
    start_index = random.randint(0, 900)

    params = {
        "title": keyword,
        "subject": keyword,
        "cnt": count,
        "start": start_index,
        "format": "xml"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        print("[DEBUG] NDL API応答（先頭500文字）:", response.text[:500])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] NDL APIリクエスト失敗: {e}")
        return []

    try:
        data = xmltodict.parse(response.text)
        items = data.get('rss', {}).get('channel', {}).get('item')

        if not items:
            print("[INFO] 検索結果なし")
            return []

        if isinstance(items, dict):
            items = [items]

        books = []
        for item in items:
            title = item.get("title", "タイトル不明")
            author = item.get("dc:creator") or item.get("author") or "著者不明"
            books.append({
                "title": title,
                "author": author
            })

        print(f"[INFO] 取得件数: {len(books)}")
        return books

    except Exception as e:
        print(f"[ERROR] XMLパース失敗: {e}")
        return []