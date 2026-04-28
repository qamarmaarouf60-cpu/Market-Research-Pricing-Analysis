import os, sys, django, re

# ajouter le dossier backend/ au path Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.products.models import Product
from scraping.spiders.jumia import fetch_jumia_search
from scraping.parsers.jumia_parser import parse_jumia

def extract_price(price_str):
    numbers = re.findall(r"[\d,.]+", price_str or "")
    if numbers:
        return float(numbers[0].replace(",", ""))
    return 0.0

query = input("🔎 Produit à rechercher : ")

html_pages = fetch_jumia_search(query=query, max_pages=2)
print(f" {len(html_pages)} pages récupérées")

products = parse_jumia(html_pages)
print(f" {len(products)} produits extraits")

created_count = 0
for item in products:
    obj, created = Product.objects.get_or_create(
        url=item["url"],
        defaults={
            "name":        item["name"],
            "price_text":  item["price"],
            "price_value": extract_price(item["price"]),
            "source":      item["source"],
            "query":       query,
        }
    )
    if created:
        created_count += 1

print(f" {created_count} nouveaux produits sauvegardés")
print(f" Total en base : {Product.objects.count()} produits")