import csv
import random
from datetime import date, timedelta

random.seed(42)

stores = ["S001", "S002", "S003"]

products = {
    "P001": 8,
    "P002": 4,
    "P003": 7,
    "P004": 5,
    "P005": 3,
    "P006": 4,
    "P007": 10,
    "P008": 12,
    "P009": 6,
    "P010": 4,
    "P011": 10,
    "P012": 15,
    "P013": 5,
    "P014": 6,
    "P015": 7,
    "P016": 5,
    "P017": 4,
    "P018": 2,
    "P019": 5,
    "P020": 7,
}

start_date = date(2026, 8, 1)

rows = []

for day_number in range(35):
    current_date = start_date + timedelta(days=day_number)

    for store in stores:
        for product_id, base_sales in products.items():

            sales = max(0, int(random.gauss(base_sales, base_sales * 0.25)))

            # P002: sales spike in the last 7 days
            if product_id == "P002" and day_number >= 28:
                sales = int(sales * 2.2)

            # P004: sales drop in the last 7 days
            if product_id == "P004" and day_number >= 28:
                sales = max(0, int(sales * 0.35))

            # P018: slow-moving product
            if product_id == "P018":
                sales = random.choice([0, 0, 1, 1, 2])

            # P012: consistently high sales
            if product_id == "P012":
                sales = max(5, int(random.gauss(15, 3)))

            # Small store-specific differences
            if store == "S002":
                sales = max(0, int(sales * 0.9))

            if store == "S003":
                sales = max(0, int(sales * 1.1))

            rows.append([
                current_date.isoformat(),
                store,
                product_id,
                sales
            ])

with open("data/sales.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "date",
        "store_id",
        "product_id",
        "units_sold"
    ])

    writer.writerows(rows)

print(f"Created data/sales.csv with {len(rows)} sales records.")