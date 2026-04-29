from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.amazon.fr"

def parse_amazon(html_pages):
    results = []

    for html in html_pages:
        soup = BeautifulSoup(html, "html.parser")
        
        products = soup.find_all("div", attrs={"data-component-type": "s-search-result"})

        for product in products:
            try:
                # 1. Nom : on cherche de manière plus large
                name_tag = product.select_one("h2 span.a-text-normal") or product.select_one("h2 span")
                name = name_tag.text.strip() if name_tag else None

                # 2. URL : on cherche le lien principal
                link_tag = product.select_one("h2 a") or product.select_one("a.a-link-normal.s-no-outline")
                link = link_tag["href"] if link_tag else None

                # 3. Image : standard Amazon
                img_tag = product.select_one("img.s-image")
                img_url = img_tag.get("src") if img_tag else None

                # 4. Prix : Amazon le cache parfois
                price_tag = product.select_one("span.a-price span.a-offscreen")
                price = price_tag.text.strip() if price_tag else "0 €" # Si pas de prix (rupture de stock), on met 0

                # On vérifie juste qu'on a le nom et le lien. 
                if not name or not link:
                    continue

                full_link = urljoin(BASE_URL, link) if not link.startswith("http") else link

                results.append({
                    "name": name,
                    "price": price,
                    "url": full_link,
                    "image_url": img_url, 
                    "source": "Amazon"
                })

            except Exception as e:
                print(f"Erreur sur un produit: {e}")
                continue

    return results