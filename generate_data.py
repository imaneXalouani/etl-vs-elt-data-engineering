import csv
import random
from datetime import datetime, timedelta

random.seed(42)

N_ROWS = 20000

cities = ["Casablanca", "casablanca", "CASABLANCA", "Rabat", "rabat", "Marrakech",
          "Tanger", "Fes", "fes ", "Agadir", None, "  Rabat  "]
categories = ["Electronique", "Textile", "Alimentaire", "Cosmetique", "Maison",
              "electronique", None, "TEXTILE"]
payment_methods = ["carte", "especes", "virement", "CARTE", None, "Carte "]
channels = ["web", "mobile", "boutique", "Web", None]

start_date = datetime(2024, 1, 1)

rows = []
for i in range(1, N_ROWS + 1):
    order_id = i
    if random.random() < 0.03 and rows:
        rows.append(rows[random.randint(0, len(rows) - 1)])
        continue

    customer_id = random.randint(1000, 6000)
    order_date = start_date + timedelta(days=random.randint(0, 540),
                                         seconds=random.randint(0, 86399))
    date_str = order_date.strftime(random.choice(["%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d"]))

    quantity = random.choice([1, 1, 1, 2, 2, 3, 4, -1])
    unit_price = round(random.uniform(20, 2500), 2)
    price_val = "" if random.random() < 0.04 else unit_price

    discount_pct = random.choice([0, 0, 0, 5, 10, 15, 20, None])
    city = random.choice(cities)
    category = random.choice(categories)
    payment = random.choice(payment_methods)
    channel = random.choice(channels)

    email = f"client{customer_id}@mail.com" if random.random() > 0.02 else ""

    rows.append([
        order_id, customer_id, date_str, category, quantity, price_val,
        discount_pct, city, payment, channel, email
    ])

with open("raw_orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "order_date", "category", "quantity",
                      "unit_price", "discount_pct", "city", "payment_method",
                      "channel", "customer_email"])
    writer.writerows(rows)

print(f"raw_orders.csv genere avec {len(rows)} lignes (dont doublons et valeurs sales volontaires).")