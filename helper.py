
MAX_CONTENT_CHARACTER_COUNT = 500

def trim_results(results: list[dict]) -> list[dict]:
    """Trim content to only what the model needs and capping content length"""

    return [
        {
           "title": r.get("title", ""),
           "url": r.get("url", ""),
           "content": (r.get("content") or "")[:MAX_CONTENT_CHARACTER_COUNT],
        }
        for r in results
    ]