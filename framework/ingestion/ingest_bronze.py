import os
import csv
import glob
import json
from datetime import datetime, timezone

from databricks import sql


def env(name: str, default: str | None = None) -> str:
    """Read required env var or return default."""
    value = os.environ.get(name, default)
    if value is None or value == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    # --- Required connection params (from GitHub Secrets) ---
    host = env("DATABRICKS_HOST")              # e.g. dbc-xxx.cloud.databricks.com
    http_path = env("DATABRICKS_HTTP_PATH")    # e.g. /sql/1.0/warehouses/xxx
    token = env("DATABRICKS_TOKEN")

    # --- Pipeline params ---
    csv_dir = os.environ.get("CSV_DIR", "data/source")
    target_table = os.environ.get("TARGET_TABLE", "gameday.bronze_customers")
    source_name = os.environ.get("SOURCE_NAME", "github_actions")

    print("=== Bronze ingestion starting ===")
    print(f"CSV_DIR       : {csv_dir}")
    print(f"TARGET_TABLE  : {target_table}")
    print(f"SOURCE_NAME   : {source_name}")
    print(f"DATABRICKS_HOST: {host}")
    print(f"HTTP_PATH     : {http_path}")

    # Lee todos los lotes (*.csv) de la carpeta: cada corrida recarga todo
    csv_files = sorted(glob.glob(os.path.join(csv_dir, "*.csv")))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in '{csv_dir}'. "
            "Verify the folder exists in the repo and CSV_DIR env is correct."
        )

    ingest_ts = datetime.now(timezone.utc).isoformat()

    rows_to_insert: list[tuple[str, str, str]] = []
    for csv_path in csv_files:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"{csv_path} has no header row. Please include column names in the first row.")

            for row in reader:
                # Store row as JSON string (raw bronze)
                raw_payload = json.dumps(row, ensure_ascii=False)
                rows_to_insert.append((ingest_ts, f"{source_name}:{os.path.basename(csv_path)}", raw_payload))
        print(f"Read {csv_path}")

    if not rows_to_insert:
        print("No data rows found in CSV. Nothing to insert.")
        return

    print(f"Rows to insert: {len(rows_to_insert)}")

    # Connect and insert (executemany uses parameterized query)
    with sql.connect(
        server_hostname=host,
        http_path=http_path,
        access_token=token,
    ) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                f"INSERT INTO {target_table} (ingest_ts, source, raw_payload) VALUES (?, ?, ?)",
                rows_to_insert
            )

    print(f"✅ Inserted {len(rows_to_insert)} rows into {target_table}")
    print("=== Bronze ingestion finished ===")


if __name__ == "__main__":
    main()
