import time
import sqlite3
import pandas as pd
import numpy as np

t0 = time.time()

# ---------- 1. EXTRACT ----------
df = pd.read_csv("raw_orders.csv")
n_raw = len(df)

# ---------- 2. TRANSFORM ----------
df = df.drop_duplicates(subset="order_id", keep="first")

def parse_date(value):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["order_date"] = df["order_date"].apply(parse_date)  # type: ignore[arg-type]
df = df.dropna(subset=["order_date"])

for col in ["city", "category", "payment_method", "channel"]:
    df[col] = df[col].astype(str).str.strip().str.lower()
    df[col] = df[col].replace({"none": np.nan, "nan": np.nan, "": np.nan})

df = df[df["quantity"] > 0]
df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
df = df.dropna(subset=["unit_price"])
df["discount_pct"] = df["discount_pct"].fillna(0)

df["customer_email"] = df["customer_email"].astype(str)
df = df[df["customer_email"].str.contains("@", na=False)]

df["revenue_ht"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
df["order_month"] = df["order_date"].dt.to_period("M").astype(str)

df_clean = df[[
    "order_id", "customer_id", "order_date", "category", "quantity",
    "unit_price", "discount_pct", "revenue_ht", "city", "payment_method",
    "channel", "order_month"
]].copy()

n_clean = len(df_clean)
t_transform = time.time()

# ---------- 3. LOAD ----------
conn = sqlite3.connect("etl_warehouse.db")
df_clean.to_sql("fact_orders", conn, if_exists="replace", index=False,
                 dtype={"order_date": "TEXT"})
conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_month ON fact_orders(order_month)")
conn.commit()

result = conn.execute(
    "SELECT order_month, ROUND(SUM(revenue_ht),2) as revenue "
    "FROM fact_orders GROUP BY order_month ORDER BY order_month LIMIT 5"
).fetchall()
conn.close()

t1 = time.time()

print("=== PIPELINE ETL (Python/Pandas -> SQLite) ===")
print(f"Lignes brutes extraites      : {n_raw}")
print(f"Lignes chargees (apres T)    : {n_clean}  ({n_raw - n_clean} rejetees/dedupliquees)")
print(f"Temps transformation (T)     : {t_transform - t0:.3f} s")
print(f"Temps total ETL (E+T+L)      : {t1 - t0:.3f} s")
print("Apercu agregat (controle) :", result)

with open("etl_metrics.txt", "w") as f:
    f.write(f"n_raw={n_raw}\nn_clean={n_clean}\ntime_transform={t_transform - t0:.4f}\ntime_total={t1 - t0:.4f}\n")