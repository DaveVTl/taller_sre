import os
from databricks import sql

HOST = os.environ["DATABRICKS_HOST"]
HTTP_PATH = os.environ["DATABRICKS_HTTP_PATH"]
TOKEN = os.environ["DATABRICKS_TOKEN"]

SCHEMA = os.environ.get("SCHEMA", "gameday")
# Política FinOps: toda tabla Gold debe tener estos tags
REQUIRED_TAGS = [t.strip() for t in os.environ.get("REQUIRED_TAGS", "owner").split(",") if t.strip()]


def main():
    with sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=TOKEN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = ? AND table_name LIKE 'gold%'",
                (SCHEMA,),
            )
            gold_tables = [r[0] for r in cur.fetchall()]

            cur.execute(
                "SELECT table_name, tag_name, tag_value FROM information_schema.table_tags WHERE schema_name = ?",
                (SCHEMA,),
            )
            tags = {}
            for table, name, value in cur.fetchall():
                tags.setdefault(table, {})[name] = value

    if not gold_tables:
        raise SystemExit(f"❌ No hay tablas Gold en {SCHEMA}. ¿Corrió el pipeline?")

    faltan = []
    for table in gold_tables:
        presentes = tags.get(table, {})
        for tag in REQUIRED_TAGS:
            if not presentes.get(tag):
                faltan.append(f"{SCHEMA}.{table} sin tag '{tag}'")
            else:
                print(f"✅ {SCHEMA}.{table}: {tag} = {presentes[tag]}")

    if faltan:
        for f in faltan:
            print(f"❌ {f}")
        raise SystemExit("❌ Política de tags: sin dueño no se publica")

    print("✅ Todas las tablas Gold tienen dueño")


if __name__ == "__main__":
    main()
