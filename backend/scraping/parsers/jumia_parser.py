from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.jumia.ma"

def parse_jumia(html_pages):
    results = []

    for html in html_pages:
        soup = BeautifulSoup(html, "html.parser")
        products = soup.select("article.prd")

        for product in products:
            try:
                name = product.select_one("h3.name")
                price = product.select_one(".prc")
                link = product.select_one("a.core")
                
                # --- NOUVEAU : Extraction de l'image ---
                img_tag = product.select_one("img.img")
                img_url = None
                if img_tag:
                    # On cherche d'abord data-src (lazy loading), sinon src
                    img_url = img_tag.get("data-src") or img_tag.get("src")

                if not name or not price:
                    continue

                raw_link = link["href"] if link else None
                full_link = urljoin(BASE_URL, raw_link) if raw_link else None

                results.append({
                    "name": name.text.strip(),
                    "price": price.text.strip(),
                    "url": full_link,
                    "image_url": img_url, # Ajout de l'image ici
                    "source": "Jumia"
                })

            except:
                continue

    return results