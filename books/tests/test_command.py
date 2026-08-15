import pytest
from decimal import Decimal
from django.core.management import call_command
from books.models import Book
from books.management.commands import scrape as scrape_command

FAKE_PAGES = {
    1: [
        {
            "title": "Fake Book",
            "url": "https://books.toscrape.com/catalogue/fake/index.html",
            "image_url": "https://books.toscrape.com/media/fake.jpg",
            "price": Decimal("12.34"),
        }
    ],
}

@pytest.fixture
def no_network(monkeypatch):
    def fake_scrape_page(url):
        page = int(url.split("page-")[1].split(".")[0])
        return FAKE_PAGES.get(page, [])

    monkeypatch.setattr(scrape_command, "scrape_page", fake_scrape_page)
    monkeypatch.setattr(scrape_command.time, "sleep", lambda seconds: None)

@pytest.mark.django_db
def test_command_stores_books(no_network):
    call_command("scrape")
    assert Book.objects.count() == 1
    assert Book.objects.first().price == Decimal("12.34")

@pytest.mark.django_db
def test_command_is_dependent(no_network):
    call_command("scrape")
    call_command("scrape")
    assert Book.objects.count() == 1