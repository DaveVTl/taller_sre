# Runbook: <nombre del incidente>

> Un runbook es lo que haría cualquier persona del equipo si esto vuelve a
> pasar a las 3 a. m. Escríbanlo para alguien que no estuvo hoy.

## Cómo me doy cuenta

- ¿Qué señal o alerta lo muestra? ¿Qué query o tabla revisan primero?
- [ ... ]

## Contener (que no empeore)

- ¿Qué apagan o retienen para no publicar más datos malos? ¿Cómo lo hacen?
- [ ... ]

## Recuperar

1. Código: [ ¿qué commit revierten y con qué comando? ]
2. Datos: [ ¿a qué versión vuelven las tablas, o qué registros corrigen? ¿con qué comando? ]
3. Reproceso: [ ¿qué reprocesan y cómo saben que no duplica? ]
4. Pendientes: [ ¿qué lote o carga retenida liberan al final? ]

## Cómo confirmo que volvimos a un estado bueno

- [ ¿qué revisan? ¿qué número debe cuadrar? ]

## A quién aviso

| Momento | A quién | Qué le digo |
| --- | --- | --- |
| Al detectar | [ ... ] | [ ... ] |
| Al recuperar | [ ... ] | [ ... ] |
