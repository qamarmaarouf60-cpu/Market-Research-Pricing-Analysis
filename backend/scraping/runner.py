import os, sys, django, re

# ajouter le dossier backend/ au path Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.products.models import Product

# Import Jumia
from scraping.spiders.jumia import fetch_jumia_search
from scraping.parsers.jumia_parser import parse_jumia

# Import Avito
from scraping.spiders.avito import fetch_avito_search
from scraping.parsers.avito_parser import parse_avito

def extract_price(price_str):
    # Enlève les espaces insécables souvent utilisés sur Avito (ex: "1 200 DH")
    price_str = price_str.replace("\xa0", "").replace(" ", "")
    numbers = re.findall(r"[\d,.]+", price_str or "")
    if numbers:
        return float(numbers[0].replace(",", ""))
    return 0.0

query = input("🔎 Produit à rechercher : ")

# --- 1. SCRAPING JUMIA ---
print("\n[1/2] --- Scraping Jumia ---")
jumia_pages = fetch_jumia_search(query=query, max_pages=10)
jumia_products = parse_jumia(jumia_pages)
print(f"✅ {len(jumia_products)} produits extraits de Jumia")

# --- 2. SCRAPING AVITO ---
print("\n[2/2] --- Scraping Avito ---")
avito_pages = fetch_avito_search(query=query, max_pages=10)
avito_products = parse_avito(avito_pages)
print(f" {len(avito_products)} produits extraits de Avito")

# --- 3. FUSION ET SAUVEGARDE ---
all_products = jumia_products + avito_products


print("\n--- Sauvegarde en base de données ---")
created_count = 0
for item in all_products:
    obj, created = Product.objects.get_or_create(
        url=item["url"],
        defaults={
            "name":        item["name"],
            "price_text":  item["price"],
            "price_value": extract_price(item["price"]),
            "image_url":   item.get("image_url"),
            "source":      item["source"],
            "query":       query,
        }
    )
    # Optionnel : si le produit existe déjà mais qu'il n'avait pas d'image, on la met à jour
    if not created and item.get("image_url") and not obj.image_url:
        obj.image_url = item.get("image_url")
        obj.save()

    if created:
        created_count += 1

print(f"🎉 {created_count} nouveaux produits sauvegardés")
print(f"📊 Total en base : {Product.objects.count()} produits")