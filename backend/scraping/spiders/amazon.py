from playwright.sync_api import sync_playwright
import time

def fetch_amazon_search(query, max_pages=10):
    html_pages = []
    base_url = f"https://www.amazon.fr/s?k={query}"

    with sync_playwright() as p:
        # On peut repasser en headless=True une fois que ça marche bien
        browser = p.chromium.launch(headless=False) 
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for p_num in range(1, max_pages + 1):
            url = f"{base_url}&page={p_num}"
            try:
                page.goto(url, timeout=60000)
                
                # ── GESTION DU BANDEAU COOKIES (Nouveau) ──
                # On essaie de voir si le bouton "Accepter les cookies" (ou refuser) est là
                try:
                    # 'sp-cc-rejectall-link' est souvent l'ID pour "Continuer sans accepter"
                    # 'sp-cc-accept' est l'ID pour "Accepter"
                    cookie_btn = page.locator("#sp-cc-accept") 
                    if cookie_btn.is_visible(timeout=3000): # On attend max 3 sec
                        print("🍪 Bandeau de cookies détecté : clic automatique !")
                        cookie_btn.click()
                        time.sleep(1) # Laisse le temps au bandeau de disparaître
                except Exception:
                    pass # Pas de cookies, on continue normalement
                # ──────────────────────────────────────────

                # On attend que les résultats de recherche s'affichent
                page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=15000)
                
                time.sleep(2) 
                
                html_pages.append(page.content())
            except Exception as e:
                print(f"⚠️ Erreur sur Amazon (page {p_num}). : {e}")
                break

        browser.close()
    return html_pages