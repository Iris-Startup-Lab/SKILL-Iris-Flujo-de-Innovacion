"""
_template_generador_skill.py

Genera el esqueleto inicial de AGENTE.md a partir de un prompt base (.md) del
flujo de innovación IRIS. Extrae Nombre, Descripción y Área/Categoría del
encabezado del prompt y produce un AGENTE.md con las secciones estándar del
template (Rol y Contexto, Alcance, Parámetros, Instrucciones, Formato de
Salida, Reglas y Restricciones, Referencias).

Uso:
    python _template_generador_skill.py <prompt.md> --skill <nombre-skill> \
        --categoria "Investigación" [--scripts] [--references] [-o <ruta>]
"""
import argparse
import os
import re
import sys


SECCIONES = [
    "# Rol y Contexto",
    "# Alcance",
    "# Parámetros de Entrada",
    "# Instrucciones",
    "# Formato de Salida",
    "# Reglas y Restricciones",
    "# Referencias",
]


def extraer_campo(texto, etiqueta):
    """Extrae el valor de una línea `**Etiqueta:** valor`."""
    patron = re.compile(r"^\s*\*{0,2}" + re.escape(etiqueta) + r"\*{0,2}\s*[:：]\s*(.*)$", re.IGNORECASE)
    for linea in texto.splitlines():
        m = patron.match(linea)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return ""


def slugify(nombre):
    s = nombre.strip().lower()
    s = re.sub(r"[^a-z0-9áéíóúüñ]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def construir_frontmatter(skill, categoria, descripcion):
    if not descripcion:
        descripcion = f"Skill del flujo de innovación IRIS (fase: {categoria or 'por definir'})."
    lineas = [
        "---",
        f"name: {skill}",
        f"description: {descripcion}",
    ]
    if categoria:
        lineas.append(f"category: {categoria}")
    lineas.append("---")
    return "\n".join(lineas) + "\n"


def construir_cuerpo(skill, con_scripts, con_references, prompt_titulo):
    refs = []
    if con_references:
        refs.append("- `references/` — taxonomías, catálogos o rúbricas vinculantes extraídas del prompt original.")
    if con_scripts:
        refs.append("- `scripts/` — scripts Python de soporte (cálculos, validación, generación de archivos).")
    if not refs:
        refs.append("- Sin referencias ni scripts: skill LLM-only (ejecución conversacional/diseño).")

    cuerpo = f"""# {skill}

> Generado desde `{prompt_titulo or 'prompt base'}`. Esqueleto a completar.

## Rol y Contexto

<!-- Qué hace el agente y con qué marco teórico. Extraer del bloque R/C del prompt. -->

## Alcance

<!-- Qué SÍ y qué NO hace (diseño vs. ejecución). Extraer del bloque "Importante — Alcance". -->

## Parámetros de Entrada

<!-- Lista de variables que el agente debe solicitar/confirmar. Extraer del bloque A. -->
<!-- Usar marcadores {{{{variable}}}} para parametrizar las instrucciones. -->

## Instrucciones

<!-- El prompt adaptado, con marcadores {{{{variable}}}}. -->

## Formato de Salida

<!-- Estructura esperada del output (markdown/csv/json/html). Extraer del bloque F. -->

## Reglas y Restricciones

<!-- Reglas de integridad, compliance, verificabilidad. -->

## Referencias

{chr(10).join(refs)}
"""
    return cuerpo


def main(argv=None):
    parser = argparse.ArgumentParser(description="Genera esqueleto de AGENTE.md desde un prompt .md")
    parser.add_argument("prompt", help="Ruta del prompt base (.md)")
    parser.add_argument("--skill", required=True, help="Nombre de la skill (kebab-case)")
    parser.add_argument("--categoria", default="", help="Fase del flujo (Investigación, Descubrimiento, etc.)")
    parser.add_argument("--scripts", action="store_true", help="La skill llevará scripts/")
    parser.add_argument("--references", action="store_true", help="La skill llevará references/")
    parser.add_argument("-o", "--output", help="Ruta de salida (por defecto: sub-skills/<skill>/AGENTE.md)")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.prompt):
        print(f"Error: no se encontró el prompt '{args.prompt}'", file=sys.stderr)
        return 1

    with open(args.prompt, encoding="utf-8") as f:
        texto = f.read()

    nombre = extraer_campo(texto, "Nombre") or os.path.splitext(os.path.basename(args.prompt))[0]
    descripcion = extraer_campo(texto, "Descripción") or extraer_campo(texto, "Descripcion")
    area = extraer_campo(texto, "Área") or extraer_campo(texto, "Area") or extraer_campo(texto, "Categoría") or extraer_campo(texto, "Categoria")
    categoria = args.categoria or area

    skill = args.skill or slugify(nombre)

    frontmatter = construir_frontmatter(skill, categoria, descripcion)
    cuerpo = construir_cuerpo(skill, args.scripts, args.references, nombre)

    salida = args.output or os.path.join("sub-skills", skill, "AGENTE.md")
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    with open(salida, "w", encoding="utf-8") as f:
        f.write(frontmatter + "\n" + cuerpo)

    print(f"AGENTE.md generado en: {salida}")
    print(f"  nombre:      {skill}")
    print(f"  categoria:   {categoria or '(no detectada)'}")
    print(f"  descripcion: {'SÍ' if descripcion else 'NO (usar genérica)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
