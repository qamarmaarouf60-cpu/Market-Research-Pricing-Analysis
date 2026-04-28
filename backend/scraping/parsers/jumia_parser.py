from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

BASE_URL = "https://www.jumia.ma"

def scrape_jumia(query: str):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Aller sur la recherche
        page.goto(f"{BASE_URL}/catalog/?q={query}", wait_until="domcontentloaded")

        # attendre produits
        page.wait_for_selector("article.prd", timeout=10000)

        products = page.query_selector_all("article.prd")

        for product in products:
            try:
                # NOM
                name_el = product.query_selector("h3.name")
                name = name_el.inner_text().strip() if name_el else None

                # PRIX
                price_el = product.query_selector(".prc")
                price = price_el.inner_text().strip() if price_el else None

                # LINK
                link_element = product.query_selector("a.core")

                if not link_element:
                      link_element = product.query_selector("a")

                link = link_element.get_attribute("href") if link_element else None

                full_link = urljoin(BASE_URL, link) if link else None

                # nettoyage du lien
                full_link = None
                if link and link.startswith("/") and "customer/account" not in link:
                    full_link = BASE_URL + link

                # éviter produits incomplets
                if not name or not price:
                    continue

                results.append({
                    "name": name,
                    "price": price,
                    "url": full_link,
                    "source": "Jumia"
                })

            except Exception:
                continue

        browser.close()

    return results