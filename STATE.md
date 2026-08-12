# STATE — Flujo de Innovación IRIS

> **Archivo generado.** No lo edites a mano: se reescribe completo en cada paso desde
> `flujo_estado.json`. Es la vista humana del estado; la fuente de verdad es el JSON.

- proyecto: (sin iniciar)
- paso_actual: (ninguno)

## Cómo iniciar

```bash
python scripts/estado_flujo.py init --proyecto "<nombre>" \
    --objetivo "<objetivo>" --audiencia "<audiencia>" [--ruta minima]
```

Eso crea `flujo_estado.json` y reescribe este archivo con la ruta, las decisiones, el
historial, los pasos omitidos con su impacto y el siguiente paso.

## Comandos del flujo

| Para | Comando (desde la raíz del repositorio) |
| --- | --- |
| Briefing del paso | `python scripts/estado_flujo.py mostrar [--paso html_N]` |
| Registrar una decisión | `... decision --paso html_N --nodo "<nodo>" --opcion "<opción>"` |
| Cerrar un paso | `... completar --paso html_N --skills <ruta> --resumen "<1 línea>" --veredicto perseverar --outputs html_N.html` |
| Omitir un paso | `... omitir --paso html_N --motivo "<motivo>"` |
| Regenerar este archivo | `... render` |

Las reglas del flujo están en `SKILL.md`; la definición de los 11 pasos, en `pasos.json`.
