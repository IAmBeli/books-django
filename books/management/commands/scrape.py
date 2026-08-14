import time
from django.core.management import BaseCommand
from books.models import Book
from books.scraper import scrape_page

class Command(BaseCommand):
    help = "Scrape books.toscrape.com and store the results"

    def handle(self, *args, **options):
        page = 1
        created_count = 0
        updated_count = 0

        while True:
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            rows = scrape_page(url)

            if not rows:
                break

            for row in rows:
                _, created = Book.objects.update_or_create(
                    url=row["url"],
                    defaults={
                        "title": row["title"], 
                        "price": row["price"],
                        "image_url": row["image_url"],
                        }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(f"Page {page} done")
            page += 1
            time.sleep(1)

        self.stdout.write(self.style.SUCCESS(
            f"Created {created_count}, updated{updated_count}"
        ))