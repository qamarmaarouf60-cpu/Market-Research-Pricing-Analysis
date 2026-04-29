from playwright.sync_api import sync_playwright
import urllib.parse

# ── CORRECTION : Format exact de la recherche Avito ──
BASE_URL = "https://www.avito.ma/fr/maroc/toutes_les_categories?q={query}&p={page}"

def fetch_avito_search(query, max_pages=10):
    all_html = []
    
    # quote_plus remplace les espaces par des '+' ("Samsung Galaxy" -> "Samsung+Galaxy")
    formatted_query = urllib.parse.quote_plus(query)

    with sync_playwright() as p:
        # Tu peux mettre headless=False si tu veux voir le navigateur
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for i in range(1, max_pages + 1):
            url = BASE_URL.format(query=formatted_query, page=i)

            print(f"🔎 [Avito] Searching: {url}")

            try:
                page.goto(url, timeout=60000)
                # Attendre un peu plus longtemps pour Avito car le site est lourd en JavaScript
                page.wait_for_timeout(4000) 
                
                all_html.append(page.content())
            except Exception as e:
                print(f" Erreur lors du chargement de la page {i} sur Avito : {e}")

        browser.close()

    return all_html