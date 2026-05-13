import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../backend/.env"))
load_dotenv()

APP_ID = os.getenv("EBAY_APP_ID")
CERT_ID = os.getenv("EBAY_CERT_ID")

def get_access_token():
    import base64
    credentials = base64.b64encode(f"{APP_ID}:{CERT_ID}".encode()).decode()
    response = requests.post(
        "https://api.sandbox.ebay.com/identity/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope",
    )
    return response.json().get("access_token")

def fetch_ebay_search(query, max_pages=3):
    print(f"🔎 [eBay API] Searching: {query}")
    token = get_access_token()
    if not token:
        print("❌ eBay: failed to get access token")
        return []

    all_items = []
    limit = 50

    for page in range(1, max_pages + 1):
        offset = (page - 1) * limit
        try:
            response = requests.get(
                "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                },
                params={
                    "q": query,
                    "limit": limit,
                    "offset": offset,
                },
            )
            data = response.json()
            items = data.get("itemSummaries", [])
            print(f"✅ [eBay API] Page {page}: {len(items)} items")
            all_items.extend(items)
            if len(items) < limit:
                break
        except Exception as e:
            print(f"❌ eBay page {page} error: {e}")

    return all_items