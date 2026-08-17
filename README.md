# books-django

A Django application that scrapes the catalogue of [books.toscrape.com](https://books.toscrape.com) into PostgreSQL and serves it as a browsable, paginated web page with an admin interface.

This is the second version of the same idea. The first, [books-scraper](https://github.com/IAmBeli/books-scraper), talks to PostgreSQL directly with hand-written SQL. This one does the same job through Django's ORM, admin and templates. Keeping both was deliberate — the interesting part is the difference between them, which is discussed below.

## What it does

```bash
python manage.py scrape     # collects 1000 books into the database
python manage.py runserver  # serves them
```

The public page shows a grid of covers with titles and prices, 20 per page, with previous/next navigation. `/admin` gives a full management interface: search, filtering, editing and deletion, behind a login.

## Project layout

```
config/          project settings, root URL table
books/
    models.py                    the Book model
    admin.py                     admin registration and list config
    views.py                     the book list view
    urls.py                      the app's URL table
    scraper.py                   HTML parsing, no Django involved
    management/commands/
        scrape.py                the manage.py scrape command
    templates/books/
        book_list.html
    static/books/
        style.css
```

`scraper.py` knows nothing about Django — it takes a URL and returns dictionaries. The management command is what connects it to the model. Splitting it that way means the parsing logic could be lifted out and reused unchanged, which is exactly what happened when it moved here from the previous project.

## The model

```python
class Book(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True, max_length=500)
    image_url = models.URLField(max_length=500, blank=True, default="")
    price = models.DecimalField(max_digits=6, decimal_places=2)
```

`price` is `DecimalField`, not `FloatField`. Floating-point values are stored approximately, which is never acceptable for money — and the value is built with `Decimal(text)` straight from the scraped string rather than passing through `float` on the way.

Uniqueness is on `url` rather than `title`. That came out of the earlier project: the catalogue contains two separate books both called *The Star-Touched Queen*, so a title-based constraint silently dropped one of them on every run. A title is a property of a book and so is a price; either makes a poor key, because it stops identifying the record as soon as the value changes. A URL is the address of one specific page, so it identifies without describing.

## Re-running the scraper

The command uses `update_or_create(url=..., defaults={...})`: a book already in the table has its fields refreshed, a new one is inserted. Running the scraper twice does not duplicate anything, and running it on a schedule would keep prices current.

Worth being honest about the cost. The raw-SQL version did this with a single statement — `INSERT ... ON CONFLICT (url) DO UPDATE` — which is one round trip per row and lets the database decide. `update_or_create` issues a `SELECT` first and then an `INSERT` or `UPDATE`, so it is two queries per row instead of one. At 1000 books behind a one-second politeness delay the difference is invisible, but it is a real illustration of what an ORM trades away: convenience for control. Django does offer `bulk_create(update_conflicts=True)` for a true upsert.

## What the ORM did better

Not everything went the other way. The migration Django generated includes an index the hand-written schema did not have:

```sql
CREATE INDEX "books_book_url_67dddeb4_like" ON "books_book" ("url" varchar_pattern_ops);
```

A plain index on a text column does not help `LIKE 'prefix%'` queries in PostgreSQL under a non-C locale; `varchar_pattern_ops` is the operator class that does. That is the kind of default an ORM supplies for free and a hand-written `CREATE TABLE` quietly omits.

Less happily, `URLField` defaults to `max_length=200`, and several book URLs on this site are longer than that. The first scrape failed on `value too long for type character varying(200)`. Framework defaults are assumptions about a typical case, and they are worth checking against real data.

## Being a good citizen

Carried over from the previous project and unchanged: a one-second delay between requests, a `User-Agent` that names the project and links to its repository rather than impersonating a browser, and `robots.txt` checked before starting. The site returns 404 for it, meaning no crawling rules are declared, and its own homepage states it exists as a scraping sandbox.

## Getting started

### 1. Database

```bash
docker run --name books-db \
  -e POSTGRES_USER=books \
  -e POSTGRES_PASSWORD=<your password> \
  -e POSTGRES_DB=booksdjango \
  -p 5432:5432 \
  --restart unless-stopped \
  -d postgres:16
```

### 2. Configuration

Copy `.env.example` to `.env` and fill it in:

```
SECRET_KEY=<a long random string>
DEBUG=True
DB_NAME=booksdjango
DB_USER=books
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```

`.env` is git-ignored. `.env.example` is committed so the required variables are documented without exposing any values — `SECRET_KEY` in particular signs sessions and CSRF tokens, and belongs nowhere near a public repository.

### 3. Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py scrape
python manage.py runserver
```

The page is at `http://localhost:8000`, the admin at `http://localhost:8000/admin`.

Requires Python 3.10 or newer.

## Tests

```bash
pytest
```

The suite covers three layers. Parsing is tested against a fixed HTML fragment rather than the live site: `scrape_page` was split into a thin network wrapper and a pure `parse_books(html, base_url)`, so the parsing logic can be checked offline, instantly, and without touching anyone's server. The model tests confirm that re-scraping a book updates it rather than inserting a duplicate. The view tests use Django's test client to check pagination, including that a malformed `?page=` value falls back gracefully instead of raising.

The management command is tested with the network call patched out, which is also the only way to assert that running the scraper twice leaves the database unchanged.

pytest-django creates and destroys a separate test database, so none of this touches development data.

## Running with Docker

The whole stack — application and database — starts with one command:

```bash
docker compose up
```

This builds the image, waits for PostgreSQL to accept connections, applies migrations, collects static files and starts gunicorn on port 8000.

Fill the database and create an admin account once the stack is running:

```bash
docker compose exec web python manage.py scrape
docker compose exec web python manage.py createsuperuser
```

Database credentials and `SECRET_KEY` come from `.env`, which compose substitutes into the container's environment. The file is deliberately excluded from both the image and the repository, so nothing inside the image contains a password — see `.env.example` for the variables that need setting.

Two details in the compose file are worth pointing out. The application reaches the database at the host `db`, which is the service name: compose puts both containers on one network where service names resolve as addresses, and `localhost` inside a container refers only to that container. And the database has no `ports` section, so it is reachable from the application but not from outside.

Postgres data lives in a named volume rather than inside the container, so `docker compose down` does not destroy it.

Static files are served by whitenoise rather than by the development server. Gunicorn does not serve static files at all, and neither does Django outside `runserver` — without whitenoise the CSS would 404 in exactly this setup.

## Possible extensions

- Collect the remaining fields: rating, availability, category
- Follow each book's URL to scrape its description
- Search and price filtering on the public page, driven by query parameters
- Record price history instead of overwriting, so changes over time are visible
- Tests for the parser and the view
- A Dockerfile and docker-compose so the app and database start together

## License

MIT