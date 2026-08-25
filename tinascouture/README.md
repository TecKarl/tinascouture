# Tina's Couture — Django Shop

A Django shop styled after the Tina's Couture flyer — blush pink background,
coral accents, and dusty-rose/mauve headings & buttons taken straight from
the flyer's color palette. The shop now sells two distinct kinds of
products, each with its own admin-manageable model.

## Features

- **Two product types, two models:**
  - `Apparel` — clothes & women's PJs. Name, description, price, stock, a
    main image, extra gallery photos, and **available sizes** picked from a
    row of checkboxes (S / M / L / XL) in the admin.
  - `Perfume` — perfumes & body splashes. Name, description, price, stock, a
    main image, extra gallery photos, plus optional brand and bottle volume
    (ml) fields.
- **Admin management** — add/edit/remove either type of product, adjust
  price & stock inline, toggle a product active/inactive to hide it from
  the shop, and upload extra photos via each product's inline image editor,
  all from `/admin/`.
- **Size checkboxes** — the `Size` model (S, M, L, XL) is seeded automatically
  by a migration; on the Apparel admin form it renders as a set of tickable
  checkboxes so you just check off whichever sizes are in stock for that item.
- **Shop pages** — the homepage shows Apparel and Perfumes in their own
  sections; clicking any product opens its own detail page with a large
  main photo, a grid of additional images, and (for apparel) badges for
  each available size.
- **Cart** — works across both product types at once. `+`/`−` buttons adjust
  quantity (clamped to live stock) on both the product page and the cart
  page; line totals and the cart total are calculated automatically from
  `price * quantity` for every item, whatever type it is.
- **Checkout** — stock is decremented automatically (and atomically, so it
  can't oversell) for each product when an order is placed; the cart is
  then cleared.
- **Contact info** — footer and checkout page link straight to the shop's
  WhatsApp (0206761073) and phone (0547691883), matching the flyer.

## Getting started

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate        # also seeds the S/M/L/XL sizes
python manage.py createsuperuser
python manage.py runserver
```

Then visit:

- Shop: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

For the Render deployment, including the separate splash Static Site and
backend Web Service, follow the repository-level `DEPLOYMENT_GUIDE.md`.

Create your own administrator with `createsuperuser`. Do not depend on a
starter account or commit a production password to the project.

## Adding products

**Apparel:**
1. Go to `/admin/`, log in, click **Apparel → Add apparel**.
2. Fill in name, description, price and stock, and upload a main image.
3. Under **Available sizes**, tick every size (S/M/L/XL) currently in stock.
4. Scroll down to the **Apparel images** inline section to add extra photos.
5. Save — it appears in the "Clothes & Women's PJs" section on the shop.

**Perfumes:**
1. Go to `/admin/`, click **Perfumes → Add perfume**.
2. Fill in name, brand, description, price, stock and volume (ml), and
   upload a main image.
3. Add extra photos in the **Perfume images** inline section.
4. Save — it appears in the "Perfumes & Body Splashes" section on the shop.

## Project layout

```
tinascouture/         Django project settings & root urls
shop/                  The shop app: models, views, admin, cart logic
  models.py            Size, Apparel, ApparelImage, Perfume, PerfumeImage
  cart.py              Session-based Cart class (handles both product types)
  views.py             Gallery, apparel/perfume detail, cart, checkout
  admin.py              Admin config (checkbox sizes, inline images)
  migrations/0002_seed_sizes.py   Seeds S / M / L / XL on first migrate
  templates/shop/       index, product_detail, cart, checkout_success
templates/base.html     Shared layout/header/footer (brand palette lives here)
media/                  Uploaded product images (created at runtime)
```

## Color palette

Sampled directly from the flyer:

| Token               | Hex       | Used for                              |
|---------------------|-----------|----------------------------------------|
| `brand-bg`           | `#f3e2e2` | Page background                        |
| `brand-ring`         | `#e9d3d5` | Light circular accents / soft panels   |
| `brand-blush`        | `#e0b9ba` | Borders, card outlines                 |
| `brand-coral`        | `#ea9e9e` | "We sell" badges, size chips           |
| `brand-mauve`        | `#a87272` | Headings, buttons, links               |
| `brand-mauveDark`    | `#8a5b5b` | Hover states                           |
| `brand-mauveDeep`    | `#6d4747` | Body text                              |
| `brand-cream`        | `#fdf6f4` | Text on dark/mauve backgrounds         |
