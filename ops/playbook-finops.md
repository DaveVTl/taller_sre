# Playbook FinOps: pipeline de contactables por país

> No buscamos la cifra exacta: buscamos que sepan de dónde sale el costo,
> quién es el dueño y qué decisión tomarían.
>
> **Supuestos de tarifa (iguales para todos):** [ los da la docente en clase ]

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

- ¿Quién usa `gold_contactables_por_pais`? ¿Quién debería responder por su costo? [ ... ]
- ¿Cómo lo dejan marcado en la tabla? [ ... ]

## 4. ¿Qué deciden?

> Busquen en el repo algo que cueste sin generar valor (pista: miren cuándo se
> dispara el pipeline y qué hace cada stage en cada corrida).

| Costo oculto que encontramos | Decisión (apagar / ajustar / priorizar) | Dueño | Fecha |
| --- | --- | --- | --- |
| [ ... ] | [ ... ] | [ ... ] | [ ... ] |

Bonus (opcional): implementen la decisión en el workflow y muestren la diferencia.
