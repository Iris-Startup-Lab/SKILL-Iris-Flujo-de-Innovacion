"""
invariante_clasificacion.py

Única implementación del invariante de clasificación de AGENTE.md sobre los
JSON de Fases 1-3:

- clasificacion_hipotesis_previa != "señal débil" => escala_a_fase4 = false.
  (toda señal/cruce con clasificación "confirmacion" o "tension" se escribe
  con escala_a_fase4: false; no compite en Fase 3 ni aparece en el HTML).
- Ningún cruce transpoblacional tiene escala_a_fase4 = true.

Compartida por:
- scripts/validar_reporte.py  -> gate final de Fase 4.
- scripts/validar_esquema.py  -> gate intermedio al cierre de Fases 1, 2 y 3.

Mantener aquí hace que ambos gates usen exactamente la misma regla: un solo
lugar para editar, cero divergencias. Este módulo es ligero y sin dependencias
externas (no importa bs4).
"""

CLASIFICACIONES_VALIDAS = {"confirmacion", "señal débil", "tension"}

FASES_CON_ITEMS = {
    "fase-1-eda-cuantitativo": "senales",
    "fase-2-eda-cualitativo": "senales",
    "fase-3-cruce": "cruces",
}


def items_de_fase(data):
    """Devuelve los items (señales/cruces) de un JSON de Fases 1-3."""
    items_key = FASES_CON_ITEMS.get(data.get("fase", ""))
    if not items_key:
        return []
    items = []
    for bloque in data.get("datos", {}).get("bloques", []):
        items.extend(bloque.get(items_key, []))
    return items


def verificar_invariante(data, ruta):
    """Devuelve lista de mensajes (nivel, texto) del invariante para un JSON.

    nivel: "ERROR" | "WARN". Los ERROR bloquean el gate; los WARN advierten.
    """
    hallazgos = []
    for item in items_de_fase(data):
        clasif = item.get("clasificacion_hipotesis_previa")
        escala = item.get("escala_a_fase4")
        item_id = item.get("id", "?")
        if clasif in ("confirmacion", "tension") and escala is True:
            hallazgos.append((
                "ERROR",
                f"{ruta}: {item_id} tiene clasificacion '{clasif}' pero escala_a_fase4=true "
                f"(Filtro 2 de AGENTE.md: no escala como señal débil)",
            ))
        elif clasif not in CLASIFICACIONES_VALIDAS and clasif is not None:
            hallazgos.append((
                "WARN",
                f"{ruta}: {item_id} tiene clasificación inválida '{clasif}'",
            ))
        if item.get("tipo_cruce") == "transpoblacional" and escala is True:
            hallazgos.append((
                "ERROR",
                f"{ruta}: {item_id} es transpoblacional y tiene escala_a_fase4=true "
                f"(blindaje de cruces transpoblacionales)",
            ))
    return hallazgos
