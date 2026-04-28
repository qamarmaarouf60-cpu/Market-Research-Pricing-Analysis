import os
import django
import re

# 1. IMPORTANT : activer Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# 2. imports Django après setup
from apps.products.models import Product
from scraping.spiders.jumia import fetch_jumia_html
from scraping.parsers.jumia_parser import parse_jumia


# 3. fonction nettoyage prix
def extract_price(price_str):
    numbers = re.findall(r"[\d,.]+", price_str)
    if numbers:
        return float(numbers[0].replace(",", ""))
    return 0.0


# 4. pipeline principal
html = fetch_jumia_html()
products = parse_jumia(html)

print(f"{len(products)} produits trouvés")

for item in products:
    Product.objects.create(
        name=item["name"],
        price_text=item["price"],
        price_value=extract_price(item["price"]),
        source=item["source"],
        url=item["url"]
    )

print("Données enregistrées en base avec succès")