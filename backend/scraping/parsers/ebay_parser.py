def parse_ebay(items):
    results = []
    for item in items:
        try:
            name = item.get("title", "")
            price_info = item.get("price", {})
            price_value = float(price_info.get("value", 0))
            currency = price_info.get("currency", "USD")
            price_text = f"{price_value} {currency}"
            url = item.get("itemWebUrl", "")
            image = item.get("image", {}).get("imageUrl", "")

            if not name or not price_value:
                continue

            results.append({
                "name": name,
                "price": price_text,
                "price_value": price_value,
                "url": url,
                "image_url": image,
                "source": "eBay",
            })
        except Exception:
            continue
    return results