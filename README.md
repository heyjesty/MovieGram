# MovieGram

An online store for buying movies and TV series, built with Django. Customers can browse and search the catalogue, add titles to a cart, check out and see their order history. Staff manage titles, categories, languages and orders from a dashboard.

## Features

- Responsive storefront with a featured-title carousel, category shelves, search, language filters and sorting
- Customer accounts using Django's authentication (hashed passwords)
- Per-user cart and checkout, plus an order history page; titles you already own can't be bought twice
- Staff dashboard at `/dashboard/` for managing titles (with poster upload), categories, languages and orders
- Django admin at `/admin/`

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate        # creates db.sqlite3 and seeds the catalogue
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000. To use the dashboard, sign in at http://127.0.0.1:8000/dashboard/ with the superuser.

Run the tests with `python manage.py test`.

## Deploying to Vercel

The project is set up for Vercel's Python runtime (`vercel.json`, entry point `Moviegram/wsgi.py`). Static files are served by WhiteNoise.

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Required in production. Use a long random string. |
| `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD` / `DJANGO_SUPERUSER_EMAIL` | Optional. Creates a staff account on startup. |
| `DATABASE_URL` | Optional. A Postgres URL (for example from Neon) for permanent storage. |
| `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` | Optional. Comma-separated, needed for custom domains. |
| `DJANGO_DEBUG` | Set to `1` to turn on debug mode. Off on Vercel by default. |

**Storage on Vercel:** without `DATABASE_URL`, each server instance builds its own SQLite database in `/tmp` from the seeded catalogue. That's fine for a demo, but new accounts, orders and uploaded posters are lost when the instance is recycled. For permanent data, set `DATABASE_URL` to a Postgres database. Uploaded posters also need external file storage, such as Vercel Blob or Cloudinary.
