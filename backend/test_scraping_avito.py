from scraping.spiders.avito import fetch_avito_search
from scraping.parsers.avito_parser import parse_avito

query = input("Enter product (Avito): ")

html_pages = fetch_avito_search(query)
data = parse_avito(html_pages)

print(f"\nResults for: {query}\n")

for p in data[:20]:
    print({
        "name": p["name"],
        "price": p["price"],
        "url": p["url"],
        "image_url": p.get("image_url"), 
        "source": p["source"]
    })