from scraping.spiders.jumia import fetch_jumia_html
from scraping.parsers.jumia_parser import parse_jumia

html = fetch_jumia_html()
data = parse_jumia(html)

print(data)