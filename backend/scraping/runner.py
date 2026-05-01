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

from scraping.spiders.ebay import fetch_ebay_search
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


def run_scraping(query, max_pages=10):
    """
    Callable by the API background thread.
    Scrapes all sources and saves to DB.
    """
    print(f"\n[Runner] Starting scraping for: '{query}'")
    all_products = []

    print(f"\n[1/4] --- Scraping Jumia ---")
    try:
        pages = fetch_jumia_search(query=query, max_pages=max_pages)
        products = parse_jumia(pages)
        print(f" {len(products)} produits extraits de Jumia")
        all_products += products
    except Exception as e:
        print(f" Jumia error: {e}")

    print(f"\n[2/4] --- Scraping Avito ---")
    try:
        pages = fetch_avito_search(query=query, max_pages=max_pages)
        products = parse_avito(pages)
        print(f" {len(products)} produits extraits de Avito")
        all_products += products
    except Exception as e:
        print(f" Avito error: {e}")

    print(f"\n[3/4] --- Scraping Amazon ---")
    try:
        pages = fetch_amazon_search(query=query, max_pages=max_pages)
        products = parse_amazon(pages)
        print(f" {len(products)} produits extraits d'Amazon")
        all_products += products
    except Exception as e:
        print(f" Amazon error: {e}")

    print(f"\n[4/4] --- Scraping eBay ---")
    try:
        pages = fetch_ebay_search(query=query, max_pages=max_pages)
        products = parse_ebay(pages)
        print(f" {len(products)} produits extraits d'eBay")
        all_products += products
    except Exception as e:
        print(f" eBay error: {e}")

    print("\n--- Sauvegarde en base de données ---")
    created_count = 0
    for item in all_products:
        if not item.get("url"):
            continue
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
    return created_count


# ── CLI usage ─────────────────────────────────────────────────
if __name__ == "__main__":
    query = input("Produit à rechercher : ")
    run_scraping(query)