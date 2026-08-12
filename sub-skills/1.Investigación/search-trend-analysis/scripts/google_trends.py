"""
google_trends.py

Consulta Google Trends vía pytrends para el experimento Search Trend Analysis.

Obtiene (datos REALES, relativos 0-100):
  - interés histórico por keyword (serie temporal)
  - promedio de interés (últimos 12 meses por defecto)
  - tendencia (pendiente de regresión lineal simple + delta primer/último)
  - queries relacionadas (top y rising) por keyword
  - desglose por región (país o región subnacional)

Limitación conocida: pytrends NO devuelve volúmenes absolutos (solo interés
relativo 0-100). Para volumen absoluto se requiere Google Keyword Planner
(fuera del alcance de este script). La skill complementa con webfetch.

Uso:
    python google_trends.py --keywords "huerto urbano,composta casera" \
        --region MX --timeframe "today 12-m" --language es-MX -o trends.json

Salida: JSON estructurado con series, promedios, tendencias y queries.
"""
import argparse
import json
import math
import sys

import pandas as pd


def _try_pytrends():
    try:
        from pytrends.request import TrendReq
        return TrendReq
    except Exception as exc:  # pragma: no cover - depende del entorno
        print(
            "ERROR: pytrends no está disponible. Instálalo con `pip install pytrends`.\n"
            f"Detalle: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)


def _serie_a_json(serie):
    """Convierte una pandas Series con índice datetime a lista de {fecha, valor}."""
    out = []
    for idx, val in serie.items():
        if isinstance(val, float) and (math.isnan(val) or val != val):
            continue
        out.append({"fecha": str(idx), "valor": round(float(val), 2)})
    return out


def _df_a_json(df):
    """DataFrame a lista de diccionarios, con NaN -> None."""
    return json.loads(df.where(pd.notna(df), None).to_json(orient="records"))


def _tendencia(serie):
    """Pendiente de regresión lineal simple normalizada por el valor medio."""
    s = serie.dropna()
    if len(s) < 2:
        return {"pendiente": None, "delta_primero_ultimo": None, "n_observaciones": int(len(s))}
    x = list(range(len(s)))
    y = s.astype(float).tolist()
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    den = sum((x[i] - mx) ** 2 for i in range(n))
    pendiente = (num / den) if den else None
    return {
        "pendiente": round(pendiente, 4) if pendiente is not None else None,
        "delta_primero_ultimo": round(float(y[-1] - y[0]), 2),
        "n_observaciones": int(len(s)),
    }


def consultar(keywords, region, timeframe, language, hl_region):
    TrendReq = _try_pytrends()
    hl = hl_region or (f"{language.split('-')[0]}-{region}" if language and region else "es-MX")
    pytrends = TrendReq(hl=hl, tz=0, timeout=(10, 25))

    geo = region or ""
    pytrends.build_payload(
        kw_list=keywords,
        cat=0,
        timeframe=timeframe,
        geo=geo,
        gprop="",
    )

    resultado = {
        "metadatos": {
            "keywords": keywords,
            "region": region or "global",
            "timeframe": timeframe,
            "language": language or "es",
            "fuente": "Google Trends (pytrends) — interés relativo 0-100, sin volúmenes absolutos",
        },
        "interes_historico": {},
        "promedio": {},
        "tendencia": {},
        "queries_relacionadas": {},
        "interes_por_region": {},
    }

    try:
        iot = pytrends.interest_over_time()
        for kw in keywords:
            if kw not in iot.columns:
                continue
            resultado["interes_historico"][kw] = _serie_a_json(iot[kw])
            resultado["promedio"][kw] = round(float(iot[kw].mean()), 2)
            resultado["tendencia"][kw] = _tendencia(iot[kw])
    except Exception as exc:
        resultado["advertencias"] = resultado.get("advertencias", []) + [
            f"interest_over_time no disponible: {exc}"
        ]

    try:
        related = pytrends.related_queries()
        for kw in keywords:
            bloque = related.get(kw, {})
            resultado["queries_relacionadas"][kw] = {
                "top": _df_a_json(bloque["top"]) if bloque.get("top") is not None else [],
                "rising": _df_a_json(bloque["rising"]) if bloque.get("rising") is not None else [],
            }
    except Exception as exc:
        resultado["advertencias"] = resultado.get("advertencias", []) + [
            f"related_queries no disponible: {exc}"
        ]

    try:
        ibr = pytrends.interest_by_region(resolution="COUNTRY", inc_low_vol=True)
        if not ibr.empty:
            resultado["interes_por_region"] = {kw: ibr[kw].to_dict() for kw in keywords if kw in ibr.columns}
    except Exception as exc:
        resultado["advertencias"] = resultado.get("advertencias", []) + [
            f"interest_by_region no disponible: {exc}"
        ]

    return resultado


def main(argv=None):
    parser = argparse.ArgumentParser(description="Consulta Google Trends vía pytrends.")
    parser.add_argument("--keywords", required=True, help="Keywords separadas por coma")
    parser.add_argument("--region", default="", help="Código de país (MX, US, etc.). Vacío = global.")
    parser.add_argument("--timeframe", default="today 12-m", help="Ej. 'today 12-m', 'today 5-y', 'today 1-m'")
    parser.add_argument("--language", default="es", help="Idioma de búsqueda (es, en, etc.)")
    parser.add_argument("--hl", default="", help="Locale del cliente (ej. 'es-MX'). Vacío = auto.")
    parser.add_argument("-o", "--output", default="trends.json", help="Ruta de salida JSON")
    args = parser.parse_args(argv)

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    if not keywords:
        print("ERROR: debe indicar al menos una keyword.", file=sys.stderr)
        return 1

    resultado = consultar(keywords, args.region, args.timeframe, args.language, args.hl)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"Datos de Google Trends guardados en: {args.output}")
    print(f"Keywords consultadas: {len(keywords)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
