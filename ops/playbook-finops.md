# Playbook FinOps: pipeline de contactables por país

> No buscamos la cifra exacta: buscamos que sepan de dónde sale el costo,
> quién es el dueño y qué decisión tomarían.
>
## 0. Supuestos de tarifa (iguales para todos)

Precios de lista públicos, revisados en octubre de 2026. Úsenlos tal cual para
que todos los equipos lleguen a números comparables.

| Recurso | Tarifa supuesta | De dónde sale |
| --- | --- | --- |
| GitHub Actions, runner Linux 2-core | USD 0.006 por minuto | Precio de lista de GitHub. **Cada job se redondea al minuto entero.** |
| Databricks SQL Warehouse serverless, 2X-Small | 4 DBU/hora × USD 0.70/DBU = **USD 2.80 por hora** | Tabla de DBU por tamaño de Databricks y tarifa Premium en AWS US East |
| Auto-stop del warehouse | 10 minutos encendido sin uso después de la última query | Valor por defecto; revisen el de su warehouse |
| Hora-persona | USD 25 por hora | Supuesto del taller |

> Ojo: en un repo **público** los minutos de Actions no se cobran, y en
> Databricks Free Edition tampoco pagan el warehouse. Calculamos con precio de
> lista porque en una empresa sí se paga.

Pistas para calcular:

- Minutos de Actions facturados = suma, por job, de su duración redondeada hacia arriba al minuto.
- Minutos de warehouse = desde la primera query hasta la última (`ops_event_log`) **más** el auto-stop.
- Comparen las dos partidas: ¿cuál pesa más y por qué?

## 1. ¿Cuánto cuesta una corrida?

| Stage | Minutos (Actions) | Minutos de warehouse (`ops_event_log`) | Costo estimado |
| --- | --- | --- | --- |
| deploy | [ ... ] | [ ... ] | [ ... ] |
| bronze | [ ... ] | [ ... ] | [ ... ] |
| ref | [ ... ] | [ ... ] | [ ... ] |
| silver | [ ... ] | [ ... ] | [ ... ] |
| validation | [ ... ] | [ ... ] | [ ... ] |
| gold | [ ... ] | [ ... ] | [ ... ] |
| tests | [ ... ] | — | [ ... ] |
| **Total por corrida** | | | [ ... ] |

- ¿Cuántas veces corre al mes? ¿Por qué se dispara? [ ... ]
- Costo mensual estimado: [ ... ]

## 2. ¿Cuánto costó el incidente?

- Corridas extra (preparar, reprocesos, pruebas): [ ... ]
- Horas-persona: [ personas ] × [ MTTR ] = [ ... ]
- ¿Cuánto habría costado recargar todo en vez de lo que hicieron? [ ... ]

## 3. ¿Quién es el dueño?

El dueño no se escribe en un Excel: se deja **en el recurso**, con tags, igual
que en Azure o AWS. Así un reporte de costos lo puede leer solo.

- ¿Quién usa `gold_contactables_por_pais`? ¿Quién debería responder por su costo? [ ... ]
- Tagueen la tabla desde el código (por ejemplo en `deploy_silver_v2.sql`, para que se aplique en cada deploy):

  ```sql
  ALTER TABLE gameday.gold_contactables_por_pais
    SET TAGS ('owner' = '[ equipo o persona ]', 'cost_center' = '[ ... ]', 'consumer' = 'marketing');
  ```

- Compruébenlo con una query, no a ojo:

  ```sql
  SELECT tag_name, tag_value
  FROM information_schema.table_tags
  WHERE schema_name = 'gameday' AND table_name = 'gold_contactables_por_pais';
  ```

- Política como código: el workflow **FinOps – Política de tags** corre después de
  cada pipeline y **falla si una tabla Gold no tiene tag `owner`**. Si lo corren hoy, sale en rojo.
  Déjenlo en verde (también lo pueden correr a mano desde Actions).

- Los tags de una tabla sirven para gobierno, pero **no** aparecen en la factura.
  Para atribuir costo, el tag va en lo que consume: el SQL Warehouse (sección
  *Tags* al editarlo). Ese tag llega a `system.billing.usage.custom_tags`.
  ¿Qué tags le pondrían al warehouse? ¿Qué pasa si dos equipos comparten el mismo? [ ... ]

## 4. ¿Qué deciden?

> Busquen en el repo algo que cueste sin generar valor (pista: miren cuándo se
> dispara el pipeline y qué hace cada stage en cada corrida).

| Costo oculto que encontramos | Decisión (apagar / ajustar / priorizar) | Dueño | Fecha |
| --- | --- | --- | --- |
| [ ... ] | [ ... ] | [ ... ] | [ ... ] |

Bonus (opcional): implementen la decisión en el workflow y muestren la diferencia.
