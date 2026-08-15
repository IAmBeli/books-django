from decimal import Decimal
from books.scraper import parse_books

BASE_URL = "https://books.toscrape.com/catalogue/page-1.html"

SAMPLE_HTML = """
<article class="product_pod">
    <div class="image_container">
        <a href="a-light-in-the-attic_1000/index.html">
            <img src="../media/cache/2c/da/cover.jpg" class="thumbnail">
        </a>
    </div>
    <h3>
        <a href="a-light-in-the-attic_1000/index.html"
           title="A Light in the Attic">A Light in the ...</a>
    </h3>
    <div class="product_price">
        <p class="price_color">£51.77</p>
    </div>
</article>
"""

def test_title_comes_from_attribute_not_truncated_text():
    rows = parse_books(SAMPLE_HTML, BASE_URL)
    assert rows[0]["title"] == "A Light in the Attic"

def test_price_is_decimal():
    rows = parse_books(SAMPLE_HTML, BASE_URL)
    assert rows[0]["price"] == Decimal("51.77")

def test_relative_links_become_absolute():
    rows = parse_books(SAMPLE_HTML, BASE_URL)
    assert rows[0]["url"].startswith("https://books.toscrape.com/")
    assert rows[0]["image_url"].startswith("https://books.toscrape.com/")

def test_page_without_books_returns_empty_list():
    assert parse_books("<html><body></body></html>", BASE_URL) == []