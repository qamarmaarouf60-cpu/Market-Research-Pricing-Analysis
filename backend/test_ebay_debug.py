from backend.scraping.spiders.ebay import fetch_ebay_search
from bs4 import BeautifulSoup

pages = fetch_ebay_search("iphone 13", max_pages=1)
soup = BeautifulSoup(pages[0], "html.parser")
print(soup.title)
print(soup.body.get_text()[:500])