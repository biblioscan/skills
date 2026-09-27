#!/usr/bin/env python3
"""Plan B quand Chasse aux Livres est inaccessible : titre, auteurs, résumé, genre.

Interroge Google Books puis Open Library. Aucune clé requise ; la variable
d'environnement GOOGLE_BOOKS_API_KEY (optionnelle) évite les limites de débit.
Usage : fetch_metadata.py <ISBN>
Sortie : JSON {"source", "title", "authors", "description", "categories"} ou {"error"}.
"""
import json
import os
import re
import sys
import urllib.request


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "biblioscan-annonce/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def google_books(isbn):
    key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    data = get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}" + (f"&key={key}" if key else ""))
    for item in data.get("items", []):
        v = item.get("volumeInfo", {})
        if v.get("title"):
            title = v["title"] + (f" - {v['subtitle']}" if v.get("subtitle") and len(v["subtitle"]) < 40 else "")
            return {
                "source": "google_books",
                "title": title,
                "authors": v.get("authors", []),
                "description": re.sub(r"<[^>]+>", "", v.get("description", "")).strip(),
                "categories": v.get("categories", []),
            }
    return None


def open_library(isbn):
    data = get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data")
    book = data.get(f"ISBN:{isbn}")
    if not book:
        return None
    desc = ""
    try:
        ed = get(f"https://openlibrary.org/isbn/{isbn}.json")
        for w in ed.get("works", [])[:1]:
            d = get(f"https://openlibrary.org{w['key']}.json").get("description", "")
            desc = d.get("value", "") if isinstance(d, dict) else d
    except Exception:
        pass
    return {
        "source": "open_library",
        "title": book.get("title", ""),
        "authors": [a["name"] for a in book.get("authors", [])],
        "description": desc.strip(),
        "categories": [s["name"] for s in book.get("subjects", [])[:5]],
    }


def main():
    isbn = re.sub(r"[^0-9Xx]", "", sys.argv[1]) if len(sys.argv) > 1 else ""
    if not isbn:
        sys.exit("usage : fetch_metadata.py <ISBN>")
    best = None
    for fn in (google_books, open_library):
        try:
            res = fn(isbn)
        except Exception as e:
            print(f"{fn.__name__} : {e}", file=sys.stderr)
            continue
        if res and res["description"]:
            best = res
            break
        best = best or res
    print(json.dumps(best or {"error": "aucune donnée trouvée"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
