#!/usr/bin/env python3
"""
dashboard_generator.py — Generador de Dashboard HTML para el Dimensionador Estratégico.

Lee los datos del análisis desde un archivo JSON y los inyecta en la plantilla
templates/reporte_template.html, produciendo un archivo HTML autónomo e interactivo.

El script busca los marcadores:
    // <!-- BEGIN_REPORT_DATA -->
    ...
    // <!-- END_REPORT_DATA -->
dentro del template y reemplaza el bloque completo de window.REPORT_DATA
con los datos reales del análisis.

Uso:
    python scripts/dashboard_generator.py --data report_data.json [--output reporte_dimensionamiento.html]
    python scripts/dashboard_generator.py  # usa datos de demo embebidos
"""

import sys
import json
import re
import argparse
from pathlib import Path

# Ruta al template relativa al directorio del script
TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "reporte_template.html"

# Marcadores de inyección en el template
MARKER_BEGIN = "// <!-- BEGIN_REPORT_DATA -->"
MARKER_END   = "// <!-- END_REPORT_DATA -->"


def load_template(template_path: Path) -> str:
    """Lee y devuelve el contenido del template HTML."""
    if not template_path.exists():
        raise FileNotFoundError(
            f"[ERROR] No se encontro el template en: {template_path}\n"
            f"Asegurate de ejecutar el script desde el directorio raiz del proyecto."
        )
    return template_path.read_text(encoding="utf-8")


def inject_data(template_html: str, report_data: dict) -> str:
    """
    Reemplaza el bloque window.REPORT_DATA en el template con los datos reales.
    
    El bloque a reemplazar esta delimitado por:
        // <!-- BEGIN_REPORT_DATA -->
        window.REPORT_DATA = window.REPORT_DATA || { ... };
        // <!-- END_REPORT_DATA -->
    
    Se sustituye por:
        // <!-- BEGIN_REPORT_DATA -->
        window.REPORT_DATA = { <datos_reales> };
        // <!-- END_REPORT_DATA -->
    """
    begin_idx = template_html.find(MARKER_BEGIN)
    end_idx   = template_html.find(MARKER_END)

    if begin_idx == -1 or end_idx == -1:
        raise ValueError(
            "[ERROR] No se encontraron los marcadores de inyeccion en el template.\n"
            f"  Buscado: '{MARKER_BEGIN}' y '{MARKER_END}'\n"
            "Verifica que templates/reporte_template.html tenga los marcadores correctos."
        )

    # Serializar los datos como JS inline con indentacion legible
    data_json = json.dumps(report_data, ensure_ascii=False, indent=2)
    
    injected_block = (
        f"{MARKER_BEGIN}\n"
        f"    window.REPORT_DATA = {data_json};\n"
        f"    {MARKER_END}"
    )

    # Calcular el indice de fin incluyendo el marcador
    end_of_block = end_idx + len(MARKER_END)

    result = template_html[:begin_idx] + injected_block + template_html[end_of_block:]
    return result


def generate_html_report(data: dict, output_path: str = "reporte_dimensionamiento.html") -> None:
    """Genera el archivo HTML final inyectando los datos en el template."""
    template_html = load_template(TEMPLATE_PATH)
    output_html   = inject_data(template_html, data)

    out = Path(output_path)
    out.write_text(output_html, encoding="utf-8")
    print(f"[OK] Dashboard HTML generado en: {out.resolve()}")


def get_default_data() -> dict:
    """Datos de demo — mismos que los de los otros generadores para coherencia de ejemplos."""
    return {
        "meta": {
            "objetivoEstrategico": "Incrementar mercado - Capturar nuevos segmentos B2B",
            "etapaNegocio": "Growth / Corporativo",
            "sector": "Fintech & Servicios Financieros B2B",
            "geografia": "Mexico / LATAM",
            "recursosPrototipado": "$45,000 USD / 90 dias de sprint",
            "criterioFit": "Sinergia con portafolio actual de pagos y payback < 9 meses"
        },
        "ideas": [
            {
                "id": "idea-1",
                "rank": 1,
                "name": "SmartB2B Checkout & Credit",
                "model": "B2B SaaS / Transaccional Hibrido",
                "ideaType": "B2B SaaS",
                "shortDesc": "Plataforma de pagos B2B con evaluacion de credito en tiempo real.",
                "score": 23,
                "verdict": "PROTOTIPAR",
                "tam": "$2.4B USD",
                "sam": "$340M USD",
                "som1y": "$8.5M USD",
                "som3y": "$42M USD",
                "som5y": "$115M USD",
                "arr1y": "$1.2M USD",
                "arr3y": "$8.5M USD",
                "arr5y": "$24M USD",
                "revenueTimeline": [1200000, 3800000, 8500000, 16000000, 24000000],
                "clvCacAdjusted": "6.8:1",
                "buyerPersonas": ["CFO Pyme Industrial", "Director de Ventas B2B"],
                "sizing": {
                    "topDown": "Mercado B2B LATAM: $12B\n-> Mexico (20%): $2.4B\n-> Vertical Industrial (25%): $600M\n-> Digitalizable Checkout (56%): $336M (SAM)",
                    "bottomUp": "12,000 Pymes Target x $2,800 USD Ticket Anual = $33.6M SAM Base",
                    "sources": "Banxico, INEGI, Statista B2B Payments 2025"
                },
                "sourcesList": [
                    {"name": "Banxico Informes Sectoriales", "url": "https://www.banxico.org.mx", "verified": True},
                    {"name": "INEGI Estadistica Industrial", "url": "https://www.inegi.org.mx", "verified": True},
                    {"name": "Statista B2B Payments 2025", "url": "https://www.statista.com", "verified": True}
                ],
                "competitors": [
                    {"name": "Credijusto / Konfio", "share": "25%", "threat": "Media", "moat": "Credito tradicional no embebido"},
                    {"name": "Clara / Tribal", "share": "18%", "threat": "Media", "moat": "Tarjetas corporativas, no facturacion proveedor"}
                ],
                "unitEconomics": [
                    {
                        "bpName": "CFO Pyme Industrial",
                        "clvBase": "$4,500 USD",
                        "crossSellBoost": "+$1,800 USD (Factoraje automatico)",
                        "clvAdjusted": "$6,300 USD (+40%)",
                        "cac": "$925 USD",
                        "clvCac": "6.8:1",
                        "payback": "4.5 meses"
                    }
                ],
                "scoreBreakdown": [
                    {"criterion": "Urgencia del problema", "points": 5, "note": "Pymes sufren falta de liquidez en ventas a 60 dias"},
                    {"criterion": "Diferenciacion", "points": 5, "note": "Algoritmo de scoring con data del SAT embebido"},
                    {"criterion": "Escalabilidad", "points": 4, "note": "Software API-first sin friccion operativa"},
                    {"criterion": "Velocidad al mercado", "points": 4, "note": "MVP integrable en 60 dias"},
                    {"criterion": "Fit estrategico", "points": 5, "note": "Alineacion total con portafolio de pagos"}
                ],
                "risks": [
                    {"risk": "Default de credito en cartera Pyme", "prob": "Media", "impact": "Alto", "level": 4,
                     "mitigation": "Garantia con seguro de credito y colateral diferido"}
                ],
                "verdictReason": "Idea lider del ciclo. Su ratio CLV:CAC de 6.8:1 impulsado por cross-selling la convierte en el candidato principal para el sprint de prototipado."
            },
            {
                "id": "idea-2",
                "rank": 2,
                "name": "Portal Copiloto Fiscal IA",
                "model": "Suscripcion B2B SaaS",
                "ideaType": "Suscripcion",
                "shortDesc": "Asistente de IA para auditoria preventiva de CFDI y conciliacion contable.",
                "score": 18,
                "verdict": "VALIDAR MAS",
                "tam": "$850M USD",
                "sam": "$120M USD",
                "som1y": "$2.8M USD",
                "som3y": "$14M USD",
                "som5y": "$38M USD",
                "arr1y": "$800K USD",
                "arr3y": "$4.2M USD",
                "arr5y": "$11.5M USD",
                "revenueTimeline": [800000, 2100000, 4200000, 7800000, 11500000],
                "clvCacAdjusted": "3.4:1",
                "buyerPersonas": ["Despachos Contables", "Contadores Independientes"],
                "sizing": {
                    "topDown": "Mercado Software Contable Mexico: $850M\n-> Despachos e Independientes (45%): $382M\n-> Accesible IA (31%): $118M (SAM)",
                    "bottomUp": "45,000 Despachos x $800 USD ARR = $36M SAM",
                    "sources": "SAT Informes Anuales, Grand View Research"
                },
                "sourcesList": [
                    {"name": "SAT Informes Anuales", "url": "https://www.sat.gob.mx", "verified": True},
                    {"name": "Grand View Research", "url": "https://www.grandviewresearch.com", "verified": True}
                ],
                "competitors": [
                    {"name": "Contpaqi / Aspel", "share": "60%", "threat": "Alta", "moat": "Distribucion masiva instalada en contadores"}
                ],
                "unitEconomics": [
                    {
                        "bpName": "Despachos Contables",
                        "clvBase": "$1,800 USD",
                        "crossSellBoost": "+$400 USD (Modulo Nomina)",
                        "clvAdjusted": "$2,200 USD (+22%)",
                        "cac": "$640 USD",
                        "clvCac": "3.4:1",
                        "payback": "9.6 meses"
                    }
                ],
                "scoreBreakdown": [
                    {"criterion": "Urgencia del problema", "points": 4, "note": "Formulas complejas de fiscalizacion en SAT"},
                    {"criterion": "Diferenciacion", "points": 3, "note": "Competidores incumbentes integrando IA rapida"},
                    {"criterion": "Escalabilidad", "points": 4, "note": "SaaS puro cloud"},
                    {"criterion": "Velocidad al mercado", "points": 4, "note": "MVP en 45 dias"},
                    {"criterion": "Fit estrategico", "points": 3, "note": "Requiere alianza con distribuidores contables"}
                ],
                "risks": [
                    {"risk": "Respuesta rapida de incumbentes (Aspel/Contpaqi)", "prob": "Alta", "impact": "Alto", "level": 5,
                     "mitigation": "Centrarse en nicho especifico de despachos medianos"}
                ],
                "verdictReason": "Atractivo alto pero requiere validar CAC en canales de adquisicion con despachos antes de construir el MVP completo."
            },
            {
                "id": "idea-3",
                "rank": 3,
                "name": "Micro-Seguros de Flete por Kilometro",
                "model": "Marketplace / Transaccional",
                "ideaType": "Marketplace",
                "shortDesc": "Poliza de seguro on-demand para transporte de carga ligera interurbana.",
                "score": 11,
                "verdict": "DESCARTAR",
                "tam": "$420M USD",
                "sam": "$45M USD",
                "som1y": "$600K USD",
                "som3y": "$3.5M USD",
                "som5y": "$9.2M USD",
                "arr1y": "$180K USD",
                "arr3y": "$950K USD",
                "arr5y": "$2.6M USD",
                "revenueTimeline": [180000, 450000, 950000, 1700000, 2600000],
                "clvCacAdjusted": "1.4:1",
                "buyerPersonas": ["Conductores de Carga Independientes"],
                "sizing": {
                    "topDown": "Seguros de Transporte Mexico: $420M\n-> Carga ligera (20%): $84M\n-> Digital accesible (50%): $42M (SAM)",
                    "bottomUp": "15,000 Transportistas x $200 USD Ticket = $3.0M SAM",
                    "sources": "AMIS Mexico"
                },
                "sourcesList": [
                    {"name": "AMIS Mexico Informes", "url": "https://www.amis.com.mx", "verified": True}
                ],
                "competitors": [
                    {"name": "Qualitas / Chubb", "share": "70%", "threat": "Alta", "moat": "Escala actuarial y licencias regulatorias"}
                ],
                "unitEconomics": [
                    {
                        "bpName": "Transportistas Independientes",
                        "clvBase": "$350 USD",
                        "crossSellBoost": "+$50 USD",
                        "clvAdjusted": "$400 USD (+14%)",
                        "cac": "$280 USD",
                        "clvCac": "1.4:1",
                        "payback": "16 meses"
                    }
                ],
                "scoreBreakdown": [
                    {"criterion": "Urgencia del problema", "points": 2, "note": "Baja disposicion a pagar en transportistas informales"},
                    {"criterion": "Diferenciacion", "points": 2, "note": "Facilmente replicable por aseguradoras"},
                    {"criterion": "Escalabilidad", "points": 2, "note": "Friccion regulatoria alta"},
                    {"criterion": "Velocidad al mercado", "points": 2, "note": "Requiere licencias de aseguradora"},
                    {"criterion": "Fit estrategico", "points": 3, "note": "Fuera del foco del portafolio"}
                ],
                "risks": [
                    {"risk": "Siniestralidad alta y regulacion CNSF", "prob": "Alta", "impact": "Alto", "level": 5,
                     "mitigation": "Descartar proyecto en este ciclo"}
                ],
                "verdictReason": "Score insuficiente (11/25). Retorno unitario insostenible (CLV:CAC 1.4:1) y barreras regulatorias elevadas."
            }
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generador de Dashboard HTML para el Dimensionador Estrategico."
    )
    parser.add_argument(
        "--data",
        help="Ruta al archivo JSON con los datos del reporte (window.REPORT_DATA schema)"
    )
    parser.add_argument(
        "--output",
        default="reporte_dimensionamiento.html",
        help="Ruta de salida del archivo .html (default: reporte_dimensionamiento.html)"
    )
    args = parser.parse_args()

    if args.data:
        try:
            with open(args.data, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[OK] Datos cargados desde: {args.data}")
        except FileNotFoundError:
            print(f"[ERROR] No se encontro el archivo: {args.data}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON invalido en {args.data}: {e}")
            sys.exit(1)
    else:
        print("[INFO] No se especifico --data. Usando datos de demo.")
        data = get_default_data()

    generate_html_report(data, args.output)


if __name__ == "__main__":
    main()
