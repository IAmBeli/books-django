import pytest
from decimal import Decimal
from books.models import Book

@pytest.fixture
def book():
    return Book.objects.create(
        title="A Light in the Attic",
        url="https://books.toscrape.com/catalogue/a-light_1000/index.html",
        image_url="https://books.toscrape.com/media/cover.jpg",
        price=Decimal("51.77"),
    )

@pytest.mark.django_db
def test_str_returns_title(book):
    assert str(book) == book.title

@pytest.mark.django_db
def test_same_url_updates_instead_of_duplicating(book):
    Book.objects.update_or_create(
        url = book.url,
        defaults={"title": book.title, "price": Decimal("49.99")},
    )

    assert Book.objects.count() == 1

    book.refresh_from_db()
    assert book.price == Decimal("49.99")