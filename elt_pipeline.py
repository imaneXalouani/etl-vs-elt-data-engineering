import time
import duckdb

t0 = time.time()

con = duckdb.connect("elt_warehouse.duckdb")

# ---------- 1. EXTRACT + 2. LOAD (brut) ----------
con.execute("DROP TABLE IF EXISTS raw_orders")
con.execute("""
    CREATE TABLE raw_orders AS
    SELECT * FROM read_csv_auto('raw_orders.csv', ALL_VARCHAR=TRUE)
""")
n_raw = con.execute("SELECT COUNT(*) FROM raw_orders").fetchone()[0]
t_load = time.time()

# ---------- 3. TRANSFORM (100% SQL) ----------
con.execute("""
    CREATE OR REPLACE VIEW stg_orders AS
    SELECT
        CAST(order_id AS INTEGER)              AS order_id,
        CAST(customer_id AS INTEGER)           AS customer_id,
        COALESCE(
            TRY_STRPTIME(order_date, '%Y-%m-%d %H:%M:%S'),
            TRY_STRPTIME(order_date, '%d/%m/%Y'),
            TRY_STRPTIME(order_date, '%Y-%m-%d')
        )                                       AS order_date,
        NULLIF(LOWER(TRIM(category)), 'none')   AS category,
        CAST(quantity AS INTEGER)               AS quantity,
        TRY_CAST(unit_price AS DOUBLE)          AS unit_price,
        COALESCE(TRY_CAST(discount_pct AS DOUBLE), 0) AS discount_pct,
        NULLIF(LOWER(TRIM(city)), 'none')       AS city,
        NULLIF(LOWER(TRIM(payment_method)), 'none') AS payment_method,
        NULLIF(LOWER(TRIM(channel)), 'none')    AS channel,
        customer_email
    FROM raw_orders
    QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_id) = 1
""")

con.execute("""
    CREATE OR REPLACE TABLE fact_orders AS
    SELECT
        order_id, customer_id, order_date, category, quantity, unit_price,
        discount_pct,
        ROUND(quantity * unit_price * (1 - discount_pct / 100.0), 2) AS revenue_ht,
        city, payment_method, channel,
        STRFTIME(order_date, '%Y-%m') AS order_month
    FROM stg_orders
    WHERE order_date IS NOT NULL
      AND quantity > 0
      AND unit_price IS NOT NULL
      AND customer_email LIKE '%@%'
""")

n_clean = con.execute("SELECT COUNT(*) FROM fact_orders").fetchone()[0]
t_transform = time.time()

result = con.execute("""
    SELECT order_month, ROUND(SUM(revenue_ht),2) as revenue
    FROM fact_orders GROUP BY order_month ORDER BY order_month LIMIT 5
""").fetchall()

con.close()
t1 = time.time()

print("=== PIPELINE ELT (CSV -> DuckDB brut -> transformation SQL) ===")
print(f"Lignes brutes chargees        : {n_raw}")
print(f"Lignes dans le mart (apres T) : {n_clean}  ({n_raw - n_clean} rejetees/dedupliquees)")
print(f"Temps chargement brut (L)     : {t_load - t0:.3f} s")
print(f"Temps transformation SQL (T)  : {t_transform - t_load:.3f} s")
print(f"Temps total ELT (E+L+T)       : {t1 - t0:.3f} s")
print("Apercu agregat (controle) :", result)

with open("elt_metrics.txt", "w") as f:
    f.write(f"n_raw={n_raw}\nn_clean={n_clean}\ntime_load={t_load - t0:.4f}\ntime_transform={t_transform - t_load:.4f}\ntime_total={t1 - t0:.4f}\n")