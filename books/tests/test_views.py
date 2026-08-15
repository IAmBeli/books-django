import pytest
from decimal import Decimal
from books.models import Book

@pytest.fixture
def many_books():
    Book.objects.bulk_create([
        Book(
            title=f"Book {i:03d}",
            url=f"https://books.toscrape.com/catalogue/book-{i}/index.html",
            price=Decimal("10.00"),
        )
        for i in range(25)
    ])

@pytest.mark.django_db
def test_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200

@pytest.mark.django_db
def test_first_page_shows_twenty_books(client, many_books):
    response = client.get("/")
    assert len(response.context["page"]) == 20

@pytest.mark.django_db
def test_second_page_shows_the_rest(client, many_books):
    response = client.get("/?page=2")
    assert len(response.context["page"]) == 5

@pytest.mark.django_db
def test_invalid_page_falls_back_off(client, many_books):
    response = client.get("/?page=abc")
    assert response.status_code == 200