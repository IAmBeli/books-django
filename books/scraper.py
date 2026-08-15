import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from decimal import Decimal

HEADERS = {
    "User-Agent": "books-django/1.0 (learning project; github.com/IAmBeli)"
}


def parse_books(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for book in soup.select("article.product_pod"):
        link = book.select_one("h3 a")
        image = book.select_one(".image_container img")
        price = book.select_one(".price_color")
        rows.append({
            "title": link["title"],
            "url": urljoin(base_url, link["href"]),
            "image_url": urljoin(base_url, image["src"]),
            "price": Decimal(price.text.replace("£", ""))
        })
    return rows

def scrape_page(url):
    response = requests.get(url, headers=HEADERS)
    response.encoding = "utf-8"
    return parse_books(response.text, url)