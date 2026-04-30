import os, sys, django, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.products.models import Product

from scraping.spiders.jumia import fetch_jumia_search
from scraping.parsers.jumia_parser import parse_jumia

from scraping.spiders.avito import fetch_avito_search
from scraping.parsers.avito_parser import parse_avito

from scraping.spiders.amazon import fetch_amazon_search
from scraping.parsers.amazon_parser import parse_amazon

# Import eBay
from backend.scraping.spiders.ebay import fetch_ebay_search
from scraping.parsers.ebay_parser import parse_ebay

def extract_price(price_str):
    price_str = price_str.replace("\xa0", "").replace(" ", "")
    price_str = price_str.replace(",", ".")
    numbers = re.findall(r"[\d.]+", price_str or "")
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return 0.0
    return 0.0

query = input("Produit à rechercher : ")

# --- 1. JUMIA ---
print("\n[1/4] --- Scraping Jumia ---")
jumia_pages = fetch_jumia_search(query=query, max_pages=10)
jumia_products = parse_jumia(jumia_pages)
print(f" {len(jumia_products)} produits extraits de Jumia")

# --- 2. AVITO ---
print("\n[2/4] --- Scraping Avito ---")
avito_pages = fetch_avito_search(query=query, max_pages=10)
avito_products = parse_avito(avito_pages)
print(f" {len(avito_products)} produits extraits de Avito")

# --- 3. AMAZON ---
print("\n[3/4] --- Scraping Amazon ---")
amazon_pages = fetch_amazon_search(query=query, max_pages=10)
amazon_products = parse_amazon(amazon_pages)
print(f" {len(amazon_products)} produits extraits d'Amazon")

# --- 4. EBAY ---
print("\n[4/4] --- Scraping eBay ---")
ebay_pages = fetch_ebay_search(query=query, max_pages=10)
ebay_products = parse_ebay(ebay_pages)
print(f" {len(ebay_products)} produits extraits d'eBay")

# --- FUSION & SAUVEGARDE ---
all_products = jumia_products + avito_products + amazon_products + ebay_products

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
    if not created and item.get("image_url") and not obj.image_url:
        obj.image_url = item.get("image_url")
        obj.save()

    if created:
        created_count += 1

print(f" {created_count} nouveaux produits sauvegardés")
print(f" Total en base : {Product.objects.count()} produits")