from scraping.spiders.jumia import fetch_jumia_search
from scraping.parsers.jumia_parser import parse_jumia

query = input("Enter product (Jumia): ")

html_pages = fetch_jumia_search(query)
data = parse_jumia(html_pages)

print(f"\nResults for: {query}\n")

for p in data[:20]:
    print({
        "name": p["name"],
        "price": p["price"],
        "url": p["url"],
        "image_url": p.get("image_url"), # <-- Ajout de l'image ici
        "source": p["source"]
    })