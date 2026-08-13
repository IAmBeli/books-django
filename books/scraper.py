import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from decimal import Decimal

HEADERS = {
    "User-Agent": "books-django/1.0 (learning project; github.com/IAmBeli)"
}


def scrape_page(url):
    response = requests.get(url, headers=HEADERS)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    rows = []
    for book in soup.select("article.product_pod"):
        link = book.select_one("h3 a")
        price = book.select_one(".price_color")
        rows.append({
            "title": link["title"],
            "url": urljoin(url, link["href"]),
            "price": Decimal(price.text.replace("£", "")),
        })
    return rows