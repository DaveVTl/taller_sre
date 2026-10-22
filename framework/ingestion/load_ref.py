import os
import csv

from databricks import sql

HOST = os.environ["DATABRICKS_HOST"]
HTTP_PATH = os.environ["DATABRICKS_HTTP_PATH"]
TOKEN = os.environ["DATABRICKS_TOKEN"]

REF_CSV = os.environ.get("REF_CSV", "data/ref/paises.csv")
TARGET_TABLE = os.environ.get("TARGET_TABLE", "gameday.ref_paises")


def main():
    # Las columnas salen del encabezado del CSV: todas como STRING
    with open(REF_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = [tuple(row[c] for c in columns) for row in reader]

    print(f"✅ Loading {REF_CSV} → {TARGET_TABLE} ({len(rows)} rows, columns={columns})")

    cols_ddl = ", ".join(f"{c} STRING" for c in columns)
    placeholders = ", ".join("?" for _ in columns)

    with sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=TOKEN) as conn:
        with conn.cursor() as cur:
            # Catálogo de referencia: se reemplaza completo en cada corrida
            cur.execute(f"CREATE OR REPLACE TABLE {TARGET_TABLE} ({cols_ddl})")
            cur.executemany(f"INSERT INTO {TARGET_TABLE} VALUES ({placeholders})", rows)

    print("✅ Reference table loaded")


if __name__ == "__main__":
    main()
