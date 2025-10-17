import requests
import xmltodict

def search_ndl_books(keyword: str, count: int = 5):
    url = "https://ndlsearch.ndl.go.jp/api/opensearch"
    params = {
        "title": keyword,
        "subject": keyword,
        "cnt": count,
        "format": "xml"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        print("[DEBUG] NDL API応答:", response.text[:500])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] NDL APIリクエスト失敗: {e}")
        return []

    try:
        data = xmltodict.parse(response.text)
        items = data.get('rss', {}).get('channel', {}).get('item')
        if not items:
            return []
        if isinstance(items, dict):
            items = [items]
        return [
            {
                "title": item.get("title", "タイトル不明"),
                "author": item.get("dc:creator") or item.get("author") or "著者不明"
            }
            for item in items
        ]
    except Exception as e:
        print(f"[ERROR] XMLパース失敗: {e}")
        return []