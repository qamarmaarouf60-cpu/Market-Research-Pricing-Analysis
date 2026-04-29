from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.avito.ma"

def parse_avito(html_pages):
    results = []

    for html in html_pages:
        soup = BeautifulSoup(html, "html.parser")
        
        # Les annonces sont toujours dans des liens <a>
        products = soup.find_all("a", href=True)

        for product in products:
            try:
                link = product["href"]
                
                # 1. Éviter les liens qui ne sont pas des annonces (boutiques, profils, etc.)
                if "avito.ma/fr/" not in link or "/boutique/" in link or "/profile/" in link:
                    continue

                img_url = None
                name = None
                
                # 2. Trouver la bonne image (et le nom)
                imgs = product.find_all("img")
                for img in imgs:
                    src = img.get("src") or img.get("data-src") or ""
                    src_lower = src.lower()
                    
                    # On ignore les avatars, les icônes, les badges et les fichiers SVG
                    if src and "avatar" not in src_lower and "icon" not in src_lower and "badge" not in src_lower and not src_lower.endswith(".svg"):
                        img_url = src
                        # ASTUCE : Sur Avito, la vraie image a presque toujours le titre exact en 'alt' !
                        name = img.get("alt")
                        break

                # 3. Récupérer tous les morceaux de texte séparément
                texts = list(product.stripped_strings)

                # Chercher le prix
                price = None
                for text in texts:
                    # Si ça contient DH et qu'il y a des chiffres
                    if "DH" in text.upper() and any(char.isdigit() for char in text):
                        price = text
                        break

                # Si le 'alt' de l'image était vide, on cherche le nom dans le texte
                if not name or len(name) < 3:
                    for text in texts:
                        text_lower = text.lower()
                        # Un vrai titre est long, ne contient pas DH, ni de date
                        if len(text) > 5 and "dh" not in text_lower and "il y a" not in text_lower and "aujourd'hui" not in text_lower and "livraison" not in text_lower:
                            name = text
                            break

                # Si on n'a vraiment ni nom, ni prix, c'est que ce n'est pas un produit
                if not name or not price:
                    continue

                raw_link = link
                full_link = urljoin(BASE_URL, raw_link) if not raw_link.startswith("http") else raw_link

                results.append({
                    "name": name.strip(),
                    "price": price.strip(),
                    "url": full_link,
                    "image_url": img_url, 
                    "source": "Avito"
                })

            except Exception as e:
                continue

    return results