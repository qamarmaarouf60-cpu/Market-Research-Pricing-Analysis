from playwright.sync_api import sync_playwright
import time

def fetch_amazon_search(query, max_pages=10):
    html_pages = []
    base_url = f"https://www.amazon.fr/s?k={query.replace(' ', '+')}"

    with sync_playwright() as p:
        # On peut repasser en headless=True une fois que ça marche bien
        browser = p.chromium.launch(headless=False) 
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        # Désactiver le flag "webdriver" pour paraître humain
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page = context.new_page()

        for p_num in range(1, max_pages + 1):
            url = f"{base_url}&page={p_num}"
            print(f"🔎 [Amazon] Searching page {p_num}: {url}")
            
            try:
                # Utiliser wait_until="networkidle" pour être sûr que tout est chargé
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                
                # Attente aléatoire pour simuler un humain
                time.sleep(3)

                # Gestion des cookies
                try:
                    if page.locator("#sp-cc-accept").is_visible(timeout=2000):
                        page.click("#sp-cc-accept")
                except:
                    pass

                # --- FIX DU SÉLECTEUR ---
                # On attend n'importe quel item de résultat, pas seulement le div spécifique
                page.wait_for_selector('.s-result-item', timeout=15000)
                
                # Scroll vers le bas pour charger les images (lazy loading)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                time.sleep(1)
                
                html_pages.append(page.content())
                
            except Exception as e:
                # Si on timeout, on vérifie si c'est un CAPTCHA
                if "captcha" in page.url or "Robot Check" in page.content():
                    print(" Bloqué par un CAPTCHA Amazon. Résous-le manuellement dans la fenêtre !")
                    time.sleep(20) # Te laisse le temps de le résoudre à la main
                else:
                    print(f" Erreur Amazon page {p_num}: {e}")
                break

        browser.close()
    return html_pages