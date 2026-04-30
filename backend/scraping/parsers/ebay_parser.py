from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

BASE_URL = "https://www.ebay.com"

def parse_ebay(html_pages):
    results = []

    for html in html_pages:
        soup = BeautifulSoup(html, "html.parser")
        listings = soup.select("li.s-item")

        for item in listings:
            try:
                # Name
                name_tag = item.select_one(".s-item__title")
                name = name_tag.get_text(strip=True) if name_tag else None
                if not name or name.lower() == "shop on ebay":
                    continue

                # Price
                price_tag = item.select_one(".s-item__price")
                price = price_tag.get_text(strip=True) if price_tag else None

                # URL
                link_tag = item.select_one("a.s-item__link")
                url = link_tag["href"] if link_tag else None

                # Image
                img_tag = item.select_one("img")
                img_url = None
                if img_tag:
                    img_url = img_tag.get("src") or img_tag.get("data-src")

                if not name or not price:
                    continue

                # Extract numeric price value
                price_clean = re.sub(r"[^\d.]", "", price.split("à")[0].split("to")[0])
                try:
                    price_value = float(price_clean)
                except ValueError:
                    price_value = 0.0

                results.append({
                    "name": name.strip(),
                    "price": price.strip(),
                    "price_value": price_value,
                    "url": url,
                    "image_url": img_url,
                    "source": "eBay"
                })

            except Exception:
                continue

    return results