from scraping.parsers.jumia_parser import scrape_jumia

query = input("🔍 Enter product: ")

data = scrape_jumia(query)

print(f"\n📦 Results for: {query}\n")

for p in data[:20]:
    print({
        "name": p["name"],
        "price": p["price"],
        "url": p["url"],
        "source": p["source"]
    })