from scraping.spiders.amazon import fetch_amazon_search
from scraping.parsers.amazon_parser import parse_amazon

query = input("Enter product (Amazon): ")

print(f"\n Lancement du scraping Amazon pour : '{query}'...")

# On limite à 1 ou 2 pages pour que le test soit rapide 
html_pages = fetch_amazon_search(query, max_pages=10) 

print(" Analyse (Parsing) des données en cours...")
data = parse_amazon(html_pages)

print(f"\n {len(data)} résultats trouvés pour : {query}\n")

# Affichage des 20 premiers résultats
for p in data[:20]:
    print({
        "name": p.get("name"),
        "price": p.get("price"),
        "url": p.get("url"),
        "image_url": p.get("image_url"), 
        "source": p.get("source")
    })