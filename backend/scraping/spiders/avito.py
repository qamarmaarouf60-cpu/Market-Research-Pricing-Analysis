from playwright.sync_api import sync_playwright
import urllib.parse

# Format typique de l'URL de recherche Avito
BASE_URL = "https://www.avito.ma/fr/maroc/{query}?p={page}"

def fetch_avito_search(query, max_pages=10):
    all_html = []
    
    # Avito gère souvent mieux les requêtes encodées (ex: "pc portable" devient "pc%20portable")
    formatted_query = urllib.parse.quote(query)

    with sync_playwright() as p:
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