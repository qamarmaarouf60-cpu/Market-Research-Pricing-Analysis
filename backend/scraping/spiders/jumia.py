from playwright.sync_api import sync_playwright

BASE_URL = "https://www.jumia.ma/catalog/?q={query}&page={page}"

def fetch_jumia_search(query, max_pages=2):
    all_html = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for i in range(1, max_pages + 1):
            url = BASE_URL.format(query=query, page=i)

            print(f"🔎 Searching: {url}")

            page.goto(url, timeout=60000)
            page.wait_for_timeout(3000)

            all_html.append(page.content())

        browser.close()

    return all_html