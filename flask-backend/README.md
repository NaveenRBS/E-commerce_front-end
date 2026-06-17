# E-Commerce Backend (Flask)

A direct port of the original Node/Express backend, rebuilt in Flask. Same
routes, same request/response shapes, same status codes - your React
frontend can talk to this without changing a single fetch call (besides
maybe the base URL).

## Why no database?

There's no user login in this app, so there's nothing that needs to be kept
separate per-user, and the only data that ever changes (the cart, and the
orders created at checkout) just needs to be shared across requests while
the server is running. Plain Python lists in memory do that perfectly well.

The trade-off: if you restart the server, the cart and orders reset back to
the seed data in `data/`. That's the same effect as calling `POST /api/reset`.
If you later want that data to survive a restart, the easiest upgrade is
SQLite (it's built into Python - no separate database server to install).
Ask if you want that version; it isn't done here on purpose.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

The server runs on **http://localhost:3000** (same default port as the
original), so if your React app already points there, nothing needs to
change.

## What's included

- `app.py` - every route, in one file, in the same order as the original
  documentation
- `data/` - the seed data (products, delivery options, default cart,
  default orders), loaded into memory on startup and reloaded on
  `POST /api/reset`
- `images/` - product images, served at `/images/...`. Skip/delete this
  folder if your React app already serves its own images from its
  `public/` folder (common in the SuperSimpleDev course setup) - nothing
  else in this backend depends on it.

## Endpoints (all under `/api`)

| Method | Path                      | Notes                                  |
|--------|---------------------------|-----------------------------------------|
| GET    | /products                 | `?search=` filters by name/keywords     |
| GET    | /delivery-options         | `?expand=estimatedDeliveryTime`         |
| GET    | /cart-items                | `?expand=product`                       |
| POST   | /cart-items                | `{ productId, quantity }`               |
| PUT    | /cart-items/:productId     | `{ quantity?, deliveryOptionId? }`      |
| DELETE | /cart-items/:productId     | -                                        |
| GET    | /orders                    | `?expand=products`, newest first        |
| POST   | /orders                    | checks out the cart, empties it         |
| GET    | /orders/:orderId           | `?expand=products`                      |
| GET    | /payment-summary           | totals for the current cart             |
| POST   | /reset                     | restores everything to seed data        |

## A note on field shapes

The original Node backend (via its ORM) actually returns a few extra
internal fields on some objects, like auto-generated timestamps. This
version matches the documented API contract exactly instead - the fields
your frontend's documentation says it can rely on - which keeps responses
cleaner without losing anything the frontend actually uses.
