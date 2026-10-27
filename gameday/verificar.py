import os
import csv
import io
import subprocess
from datetime import datetime

from databricks import sql

HOST = os.environ["DATABRICKS_HOST"]
HTTP_PATH = os.environ["DATABRICKS_HTTP_PATH"]
TOKEN = os.environ["DATABRICKS_TOKEN"]
RUN_ID = os.environ.get("RUN_ID", "manual")

SILVER = "gameday.silver_customers_v2"
GOLD = "gameday.gold_contactables_por_pais"
REF = "gameday.ref_paises"
LOG = "gameday.ops_event_log"

# Catálogo correcto: contra esto se compara producción
PAISES_OK = {
    "PE": ("Perú", "Andina"),
    "CL": ("Chile", "Cono Sur"),
    "AR": ("Argentina", "Cono Sur"),
    "CO": ("Colombia", "Andina"),
}
CLIENTES_ESPERADOS = 26  # jueves (12) + viernes (8) + lunes (6)


def rows(cur, stmt, params=None):
    cur.execute(stmt, params) if params else cur.execute(stmt)
    return cur.fetchall()


def catalogo_malo_en(sha):
    """True si en ese commit el catálogo del repo tiene algún país mal mapeado."""
    try:
        content = subprocess.run(
            ["git", "show", f"{sha}:data/ref/paises.csv"],
            capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return False
    for r in csv.DictReader(io.StringIO(content)):
        code = r.get("country_code")
        if code in PAISES_OK and (r.get("country_name"), r.get("region")) != PAISES_OK[code]:
            return True
    return False


def main():
    resultados = []  # (criterio, puntos, ok, detalle)

    with sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=TOKEN) as conn:
        with conn.cursor() as cur:
            inicio = rows(cur, f"SELECT MAX(event_ts) FROM {LOG} WHERE stage = 'incidente_inicio'")[0][0]
            if inicio is None:
                raise SystemExit("❌ No encuentro el inicio del incidente. Corran primero 'Game day – Preparar producción'.")

            # --- Recuperar (25): catálogo, Silver y Gold correctos, con el lote del lunes ---
            ref = {r[0]: (r[1], r[2]) for r in rows(cur, f"SELECT country_code, country_name, region FROM {REF}")}
            ref_ok = all(ref.get(c) == v for c, v in PAISES_OK.items())

            silver = rows(cur, f"SELECT customer_id, country_code, country_name, region, dq_status, email FROM {SILVER}")
            mal_pais = [r[0] for r in silver if PAISES_OK.get(r[1]) != (r[2], r[3])]
            ids = {r[0] for r in silver}

            esperado = {}
            for _, code, _, _, dq_status, email in silver:
                if dq_status == "FAIL_NAME_NULL" or code not in PAISES_OK:
                    continue
                pais = PAISES_OK[code]
                total, cont = esperado.get(pais, (0, 0))
                esperado[pais] = (total + 1, cont + (1 if dq_status == "PASS" and email else 0))
            gold = {(r[0], r[1]): (r[2], r[3]) for r in rows(cur, f"SELECT pais, region, clientes, contactables FROM {GOLD}")}

            recuperar_ok = ref_ok and not mal_pais and len(ids) == CLIENTES_ESPERADOS and gold == esperado
            resultados.append((
                "Recuperar", 25, recuperar_ok,
                f"catálogo {'ok' if ref_ok else 'MAL'} · clientes con país mal: {len(mal_pais)} · "
                f"clientes en Silver: {len(ids)}/{CLIENTES_ESPERADOS} · Gold {'cuadra' if gold == esperado else 'NO cuadra'}",
            ))

            # --- Sin duplicar (15): un registro por cliente en Silver ---
            duplicados = len(silver) - len(ids)
            resultados.append(("Sin duplicar", 15, duplicados == 0, f"filas duplicadas en Silver: {duplicados}"))

            # --- Contener (15): ninguna publicación a Gold con el catálogo malo después del inicio ---
            publicaciones = rows(cur, f"""
                SELECT run_id, event_ts, details FROM {LOG}
                WHERE stage = 'gold' AND status = 'success' AND event_ts > ?
            """, (inicio,))
            malas = [p for p in publicaciones if catalogo_malo_en(p[2].replace("sha=", "").strip())]
            resultados.append((
                "Contener", 15, not malas,
                f"publicaciones a Gold con el catálogo malo después del inicio: {len(malas)}",
            ))

            tecnico = sum(p for _, p, ok, _ in resultados if ok)
            # Producción está de vuelta si recuperaron sin duplicar; Contener solo suma puntos
            todo_ok = all(ok for nombre, _, ok, _ in resultados if nombre != "Contener")

            ahora = rows(cur, "SELECT current_timestamp()")[0][0]
            mttr_min = (ahora - inicio).total_seconds() / 60 if isinstance(ahora, datetime) else None

            cur.execute(
                f"INSERT INTO {LOG} VALUES (?, current_timestamp(), 'verificar', ?, ?)",
                (RUN_ID, "success" if todo_ok else "failure",
                 f"puntaje_tecnico={tecnico}; mttr_min={mttr_min:.1f}" if mttr_min is not None else f"puntaje_tecnico={tecnico}"),
            )

    lineas = ["## Game day – Verificación", "", "| Criterio | Puntos | Resultado | Detalle |", "| --- | --- | --- | --- |"]
    for nombre, pts, ok, detalle in resultados:
        lineas.append(f"| {nombre} | {pts if ok else 0}/{pts} | {'✅' if ok else '❌'} | {detalle} |")
    lineas += ["", f"**Puntaje técnico: {tecnico}/55.** Detectar (20) y Postmortem (15) los revisa la docente."]
    if mttr_min is not None:
        lineas.append(f"**Tiempo desde el inicio del incidente: {mttr_min:.1f} min.**")
    if todo_ok:
        lineas.append("🟢 Producción recuperada. Si es su primer verde, ese es su MTTR.")

    reporte = "\n".join(lineas)
    print(reporte)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(reporte + "\n")

    if not todo_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
