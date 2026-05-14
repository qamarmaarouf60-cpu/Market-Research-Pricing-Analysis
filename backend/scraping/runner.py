import os
import sys
import django
import re
import concurrent.futures
from django.db.models import Avg, Min, Max

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.products.models import Product
from apps.analytics.models import PriceSnapshot

from scraping.spiders.jumia import fetch_jumia_search
from scraping.parsers.jumia_parser import parse_jumia
from scraping.spiders.avito import fetch_avito_search
from scraping.parsers.avito_parser import parse_avito
from scraping.spiders.amazon import fetch_amazon_search
from scraping.parsers.amazon_parser import parse_amazon
from scraping.spiders.ebay import fetch_ebay_search
from scraping.parsers.ebay_parser import parse_ebay

def extract_price(price_str):
    if not price_str: return 0.0
    price_str = price_str.replace("\xa0", "").replace(" ", "").replace(",", ".")
    numbers = re.findall(r"[\d.]+", price_str)
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return 0.0
    return 0.0

def is_relevant(item, query):
    name = item.get("name", "").lower()
    main_word = query.lower().split()[0]
    return main_word in name

def scrape_source(name, fetch_func, parse_func, query, max_pages):
    print(f"--- [Début] {name} ---")
    try:
        pages = fetch_func(query=query, max_pages=max_pages)
        products = parse_func(pages)
        print(f"--- [Fin] {name} : {len(products)} produits trouvés ---")
        return products
    except Exception as e:
        print(f"!!! Erreur sur {name} : {e}")
        return []

def run_scraping(query, max_pages=10):
    print(f"\n🚀 Lancement du scraping global pour : '{query}'")

    all_products_data = []
    sources = [
        ("Jumia", fetch_jumia_search, parse_jumia),
        ("Avito", fetch_avito_search, parse_avito),
        ("Amazon", fetch_amazon_search, parse_amazon),
        ("eBay", fetch_ebay_search, parse_ebay),
    ]

    # 1. SCRAPING PARALLÈLE
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as executor:
        futures = [
            executor.submit(scrape_source, name, fetch, parse, query, max_pages)
            for name, fetch, parse in sources
        ]
        for future in concurrent.futures.as_completed(futures):
            all_products_data.extend(future.result())

    # 2. FILTRAGE PAR PERTINENCE
    filtered = [item for item in all_products_data if is_relevant(item, query)]
    print(f"🔍 {len(filtered)}/{len(all_products_data)} produits pertinents après filtrage.")

    # 3. SAUVEGARDE EN BASE DE DONNÉES
    print(f"\n💾 Sauvegarde de {len(filtered)} produits...")
    created_count = 0
    for item in filtered:
        if not item.get("url"): continue

        price_value = item.get("price_value") or extract_price(item.get("price", ""))

        obj, created = Product.objects.get_or_create(
            url=item["url"],
            defaults={
                "name": item["name"],
                "price_text": item.get("price", ""),
                "price_value": price_value,
                "image_url": item.get("image_url"),
                "source": item["source"],
                "query": query,
            }
        )
        if created: created_count += 1

    print(f"✅ {created_count} nouveaux produits ajoutés.")

    # 4. SNAPSHOT ANALYTIQUE
    print(f"\n📊 Génération des statistiques pour '{query}'...")
    stats = Product.objects.filter(query=query).aggregate(
        avg_p=Avg('price_value'),
        min_p=Min('price_value'),
        max_p=Max('price_value')
    )

    if stats['avg_p'] is not None:
        PriceSnapshot.objects.create(
            category=query,
            avg_price=round(stats['avg_p'], 2),
            min_price=round(stats['min_p'], 2),
            max_price=round(stats['max_p'], 2),
            count=Product.objects.filter(query=query).count()
        )
        print(f"📈 Snapshot enregistré.")

    print("\n🏁 Opération terminée.")