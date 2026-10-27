# Taller SRE y FinOps: game day sobre un pipeline de datos

Hoy rompemos producción, a propósito. Este repo trae el pipeline del taller DataOps funcionando y, en su historia, un cambio que salió mal. Su equipo tiene que **detectar, contener, recuperar y aprender** del incidente, y luego **ponerle precio y dueño** al pipeline.

> **Idea clave:** no se casen con ninguna herramienta. Aquí usamos Databricks y GitHub Actions como ejemplo. Lo que se queda con ustedes es el método: volver rápido, revertir sin perder trazabilidad y decidir con costos.

---

## Qué esperamos

Al terminar, su equipo puede:

1. **Recuperar con método:** detectar, contener, revertir el código y volver el dato a un estado bueno, sin duplicar.
2. **Aprender del incidente:** escribir un postmortem sin culpables y agregar un check que habría frenado el cambio.
3. **Ponerle precio y dueño:** estimar cuánto cuesta el pipeline, cuánto costó el incidente y quién responde por ese gasto.

No esperamos que construyan un pipeline nuevo, que usen herramientas pagadas ni que calculen un costo exacto.

## Qué entregan

**Un Pull Request por equipo** a la rama `main` de su fork, con:

| Archivo | Qué contiene |
| --- | --- |
| `ops/runbook.md` | Qué hacer si vuelve a pasar, paso a paso |
| `ops/postmortem.md` | Línea de tiempo, impacto, causa raíz, MTTR y acción preventiva |
| `ops/playbook-finops.md` | Costo por corrida, costo del incidente, dueño y una decisión |
| `framework/validation/validate_silver.py` | Un check nuevo que habría frenado el cambio |
| El fix | El revert del cambio y los datos recuperados, con `verificar` en verde |

**Definición de listo:** `verificar` en verde, los 3 archivos de `ops/` completos y el check nuevo.

## Roles (equipos de 3 o 4)

| Rol | Qué hace |
| --- | --- |
| **Comandante** | Decide, prioriza y controla el tiempo. No toca el teclado. |
| **Operador** | Ejecuta: queries, revert, reproceso. |
| **Comunicador** | Avisa a Marketing y escribe el postmortem mientras pasa. |

## Cómo se gana (100 puntos)

| Criterio | Puntos | Quién lo revisa |
| --- | --- | --- |
| Detectar: encuentran el cambio culpable y explican la causa raíz | 20 | La docente |
| Contener: no se publicaron más datos malos mientras arreglaban | 15 | `verificar` |
| Recuperar: catálogo, Silver y Gold correctos, con el lote del lunes cargado | 25 | `verificar` |
| Sin duplicar: un registro por cliente | 15 | `verificar` |
| Postmortem: línea de tiempo, causa raíz y acción preventiva | 15 | La docente |
| MTTR: el equipo que vuelve primero | +10 | Primer `verificar` en verde |

Cada pista que pidan a la docente cuesta 5 puntos.

---

## Estructura del repo

```
.
├── README.md                    ← este archivo
├── incidente/alerta.md          ← lo que les llega de Marketing
├── data/
│   ├── source/                  ← lotes que el pipeline carga (*.csv)
│   ├── ref/paises.csv           ← catálogo de países
│   └── incoming/                ← lotes que llegan y aún no se cargan
├── framework/                   ← el pipeline del taller DataOps (Bronze → Silver → Gold)
├── gameday/                     ← herramientas del taller (no son parte de producción)
├── ops/                         ← plantillas que ustedes completan
├── prompts.md                   ← prompts opcionales para usar la IA como copiloto
└── .github/workflows/
    ├── dataops-pipeline.yml     ← el pipeline de producción
    ├── preparar-produccion.yml  ← arma producción y empieza el incidente
    ├── verificar.yml            ← revisa si volvieron a un estado bueno
    └── finops-politica-tags.yml ← falla si una tabla Gold no tiene dueño
```

El pipeline corre por stages: `deploy → bronze + ref → silver → validation → gold`, más `tests`. Cada stage deja su registro en `gameday.ops_event_log`.

---

## Paso a paso

### 0. Antes de clase (15 min)

1. Haz **fork** de este repo (botón *Fork*).
2. En tu fork, ve a la pestaña **Actions** y pulsa **I understand my workflows, go ahead and enable them**. En un fork las Actions vienen apagadas.
3. En **Settings → Secrets and variables → Actions**, crea los mismos 3 secrets del taller DataOps:

   | Secret | Qué es |
   | --- | --- |
   | `DATABRICKS_HOST` | El host del workspace, sin `https://` |
   | `DATABRICKS_HTTP_PATH` | La ruta de tu SQL Warehouse |
   | `DATABRICKS_TOKEN` | Tu token personal |

4. Enciende tu SQL Warehouse en Databricks.

> 🔒 Nunca pegues el token en un archivo del repo ni en el chat con tu asistente.

✅ Checkpoint: Actions habilitadas y los 3 secrets creados. Todo se crea en un schema nuevo, `gameday`, así que lo del taller DataOps queda intacto.

### 1. Briefing (5 min)

Formen equipos, repartan los roles y anótenlos en `ops/postmortem.md`.

✅ Checkpoint: cada persona sabe su rol.

### 2. Preparar producción (2 min)

En **Actions → Game day – Preparar producción → Run workflow**. Deja el schema `gameday` como estaba producción el viernes en la noche. Tarda unos minutos.

Cuando termine, **empieza el reloj**. Lean [`incidente/alerta.md`](incidente/alerta.md).

✅ Checkpoint: el workflow está en verde y leyeron la alerta.

### 3. Detectar (10 min)

Preguntas guía:

- ¿Qué cambió desde el jueves? ¿Quién lo cambió y cuándo?
- ¿Qué tablas se ven afectadas y desde qué versión?
- ¿A qué clientes afectó? ¿Cuántos?
- ¿Por qué ningún check lo frenó?

Tienen el historial del repo, el historial de versiones de las tablas y `gameday.ops_event_log`.

✅ Checkpoint: anotan en el postmortem el cambio culpable y la hora en que lo encontraron.

### 4. Contener (5 min)

A los 15 minutos la docente avisa que **llegó el lote del lunes** a `data/incoming/`. El procedimiento normal es moverlo a `data/source/` y hacer push, lo que dispara el pipeline.

- ¿Lo cargan ya? ¿Qué pasa si lo hacen antes de arreglar la causa?
- ¿Cómo evitan que se publiquen más datos malos mientras arreglan?

✅ Checkpoint: decidieron qué hacer con el lote y lo anotaron en la línea de tiempo.

### 5. Recuperar (20 min)

Recuerden la lámina de reversiones: **el código vuelve, el dato no.**

1. **Código:** reviertan el cambio en un PR. No borren historia: el revert también queda en el historial.
2. **Datos:** dejen las tablas en un estado bueno. Pueden volver a una versión anterior o corregir solo lo afectado. Elijan y justifiquen.
3. **Pendientes:** carguen el lote del lunes.

Cuando crean que terminaron, corran **Actions → Game day – Verificar**. Pueden correrlo cuantas veces quieran: el resumen de la corrida les dice qué falta.

✅ Checkpoint: `verificar` en verde.

### 6. Postmortem y check nuevo (10 min)

1. Completen `ops/postmortem.md` y `ops/runbook.md`.
2. Agreguen en `framework/validation/validate_silver.py` un check que habría frenado el cambio del viernes.

✅ Checkpoint: el check nuevo falla si vuelven a aplicar el cambio del viernes.

### 7. Playbook FinOps (20 min)

Completen `ops/playbook-finops.md`, que tiene 4 preguntas sobre **este** pipeline:

1. ¿Cuánto cuesta una corrida? Usen la duración de cada job en Actions y los tiempos de `gameday.ops_event_log`.
2. ¿Cuánto costó el incidente? Corridas extra y horas-persona.
3. ¿Quién es el dueño del costo? Déjenlo en tags sobre la tabla y el warehouse, no en un documento aparte. El workflow **FinOps – Política de tags** debe quedar en verde.
4. ¿Qué deciden? Una decisión sobre un costo oculto del repo, con dueño y fecha.

✅ Checkpoint: hay al menos una decisión con dueño y fecha.

### 8. PR y debrief (8 min)

Abran el PR a `main` de su fork con la definición de listo y compartan:

- Su puntaje y su MTTR.
- Qué camino eligieron para recuperar los datos y por qué.
- Qué cambiarían para que no vuelva a pasar.

✅ Checkpoint: PR abierto con `verificar` en verde.

---

## Lo mismo en otras plataformas

| Aquí | Equivalentes |
| --- | --- |
| GitHub Actions | Azure Pipelines, GitLab CI, Jenkins |
| Historial de versiones de tablas (Delta) | Snapshots de Iceberg, time travel de Snowflake o BigQuery, backups |
| `ops_event_log` | Logs del orquestador, tablas de auditoría, observabilidad |

## Sobre la IA

`prompts.md` trae prompts opcionales para usar su asistente como copiloto. La IA sugiere; el equipo decide y verifica. Si la IA les propone un cambio, el Operador lo revisa antes de ejecutarlo.
