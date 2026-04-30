from backend.scraping.spiders.ebay import fetch_ebay_search
from scraping.parsers.ebay_parser import parse_ebay

query = input("Enter product (eBay): ")

html_pages = fetch_ebay_search(query)
data = parse_ebay(html_pages)

print(f"\nResults for: {query}\n")

for p in data[:20]:
    print({
        "name": p["name"],
        "price": p["price"],
        "url": p["url"],
        "image_url": p.get("image_url"),
        "source": p["source"]
    })