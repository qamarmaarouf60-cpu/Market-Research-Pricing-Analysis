from playwright.sync_api import sync_playwright
import urllib.parse

BASE_URL = "https://www.ebay.com/sch/i.html?_nkw={query}&_pgn={page}"

def fetch_ebay_search(query, max_pages=10):
    all_html = []
    formatted_query = urllib.parse.quote_plus(query)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
        )

        # Hide webdriver flag
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page = context.new_page()

        for i in range(1, max_pages + 1):
            url = BASE_URL.format(query=formatted_query, page=i)
            print(f"🔎 [eBay] Searching: {url}")

            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                all_html.append(page.content())
            except Exception as e:
                print(f"❌ Erreur page {i} eBay : {e}")

        browser.close()

    return all_html