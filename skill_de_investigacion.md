---
name: Fuentes de Datos Abiertos sin API Key
description: Catálogo de fuentes públicas y gratuitas de datos (macro, México, mercados, tendencias) que no requieren registro ni token, clasificadas por si son aptas para uso empresarial o requieren revisión legal previa. Úsala cuando una investigación necesite respaldar afirmaciones con datos duros, comparar México contra otros países, o consultar indicadores oficiales sin gestionar credenciales.
---

## Objetivo

Esta skill le da a Claude un mapa de qué fuente de datos abiertos consultar según el tipo de pregunta, priorizando fuentes que no requieren API key ni registro previo. Como esta skill corre en un entorno empresarial, se distingue explícitamente entre:

- **Fuentes oficiales/institucionales** — datos de dominio público gubernamental o de organismos multilaterales, publicados para reutilización libre. Seguras para uso interno y análisis empresarial sin fricción legal.
- **Librerías no oficiales (scraping)** — son keyless, pero acceden a datos de sitios cuyos Términos de Servicio restringen el uso automatizado o comercial (ej. Yahoo Finance, Google Trends). Requieren revisión de legal/compliance antes de usarse en un flujo de producción empresarial. Claude debe advertir esto explícitamente si el usuario pide datos de esta categoría.

## Cómo decidir qué fuente usar

1. **¿La pregunta compara México con otros países o regiones?** → sección 1 (multilaterales, oficiales).
2. **¿La pregunta es específica de México (economía, población, seguridad, finanzas públicas)?** → sección 2 (oficiales mexicanas, vía descarga directa, no vía API con token).
3. **¿La pregunta involucra precios de mercado (acciones, cripto, tendencias de búsqueda)?** → sección 3. **Advierte al usuario** que son fuentes no oficiales antes de usarlas para algo más que una consulta puntual de referencia.
4. **¿La pregunta necesita contexto de noticias o geolocalización?** → sección 4.

Si una fuente relevante requiere API key (ver nota al final) o cae en la categoría "no oficial", señala esa limitación en vez de inventar datos o presentarlos como si vinieran de una fuente con respaldo institucional.

---

## 1. Multilaterales — oficiales, sin key, aptas para empresa

| Fuente | Cubre | Cómo consultar |
| --- | --- | --- |
| Banco Mundial | Macro, desarrollo, pobreza (~1,500 indicadores) | `wbgapi` (Python) o API REST `api.worldbank.org/v2/` |
| FMI | Macro, balanza de pagos, deuda, proyecciones (WEO) | API pública DataMapper `imf.org/external/datamapper/api/v1/` |
| OCDE | Macro, empleo, bienestar (México es miembro) | API SDMX pública `sdmx.oecd.org/public/rest/data/` |
| BIS (Banco de Pagos Internacionales) | Estadísticas financieras/bancarias globales | API pública `stats.bis.org/api/v1/` |
| OMS (WHO GHO) | Salud pública | API REST pública `ghoapi.azureedge.net/api/` |
| FAOSTAT | Agricultura, alimentación | API pública `fenixservices.fao.org/faostat/api/v1/` |
| ILOSTAT (OIT) | Empleo, salarios, informalidad laboral | Descargas bulk o SDMX público `ilostat.ilo.org` |

## 2. México — fuentes oficiales, sin token, aptas para empresa

**Importante:** INEGI y Banxico tienen APIs "premium" que sí piden token (Banco de Indicadores / SIE). Aquí solo se listan sus canales de **descarga abierta directa**, que no requieren registro.

| Fuente | Cubre | Cómo consultar |
| --- | --- | --- |
| INEGI — Datos Abiertos | Censos, encuestas, DENUE, marco geoestadístico en archivos descargables | Portal `inegi.org.mx/datosabiertos/` y descarga masiva `inegi.org.mx/app/descarga/` (CSV/SHP/XLS directos, sin token) |
| Banxico — Portal público | Tipo de cambio, tasas, series históricas vía exportación manual/CSV | `banxico.org.mx` → sección "Consulta de Cuadros" o "SIE" (exportar sin generar token, para series puntuales) |
| CONEVAL | Pobreza, medición multidimensional, rezago social | Descargas CSV/XLSX en `coneval.org.mx` |
| CONAPO | Proyecciones de población, migración | Descargas abiertas en `gob.mx/conapo` |
| SESNSP | Incidencia delictiva por municipio/mes | CSV mensuales en `gob.mx/sesnsp` (datos abiertos de incidencia delictiva) |
| Transparencia Presupuestaria (SHCP) | Finanzas públicas, gasto federal | Portal + datasets abiertos en `transparenciapresupuestaria.gob.mx` |
| SAT | Datos abiertos de facturación/padrón | Sección de datos abiertos en `sat.gob.mx` |
| datos.gob.mx | Catálogo federal agregando ~50 dependencias (CKAN) | API pública de lectura `datos.gob.mx/api/3/action/` (no requiere key para consultas GET) |
| CNBV | Estadísticas del sistema bancario/bursátil | Portal de información estadística en `cnbv.gob.mx` |
| IMSS | Empleo formal asegurado | Datos abiertos mensuales en `gob.mx/imss` |

## 3. Mercados y tendencias — keyless, pero NO oficiales (⚠️ revisar con legal antes de producción)

Estas fuentes no requieren token porque no son APIs oficiales: son librerías que acceden a páginas públicas de terceros cuyos Términos de Servicio limitan el uso automatizado o comercial. Úsalas solo para consultas puntuales de referencia interna y avisa al usuario de esta condición si el resultado va a alimentar un entregable, reporte externo o proceso recurrente.

| Fuente | Cubre | Cómo consultar | Advertencia |
| --- | --- | --- | --- |
| Yahoo Finance | Precios de acciones/índices, incluida BMV | `yfinance` | La librería se declara "personal use only"; Yahoo prohíbe acceso automatizado sin permiso en su ToS |
| Google Trends | Interés de búsqueda por región/tiempo en México | `pytrends` | Scraper no oficial; no hay API pública sancionada por Google |
| CoinGecko | Criptomonedas | API pública `api.coingecko.com/api/v3/` | Sí es oficial, pero la licencia gratuita es para uso personal/prototipo; uso comercial formal requiere plan de pago con atribución |

Si el negocio necesita datos de mercado de forma recurrente y con respaldo contractual, la alternativa correcta es un proveedor de datos licenciado (ej. Refinitiv/LSEG, Bloomberg, FactSet, o el propio proveedor de bróker de la empresa), no estas librerías.

## 4. Complementarias — oficiales/de dominio abierto, aptas para empresa con matices

| Fuente | Cubre | Cómo consultar | Nota |
| --- | --- | --- | --- |
| GDELT | Monitoreo global de noticias/eventos, filtrable por país | API pública `api.gdeltproject.org/api/v2/doc/doc` | Proyecto académico de acceso abierto |
| OpenStreetMap / Overpass | Geolocalización, puntos de interés | `overpass-api.de/api/interpreter` | Licencia de datos ODbL (atribución requerida); respetar la política de "fair use" del servidor público, no hacer consultas masivas sin límite |
| Wikidata | Datos estructurados de entidades (empresas, personas, lugares) | SPARQL público `query.wikidata.org/sparql` | Datos bajo CC0, sin restricción de uso comercial |

---

## Buenas prácticas al usar estas fuentes

- Cita siempre la fuente y la fecha del dato (INEGI y Banxico son mensuales/trimestrales, SESNSP es mensual, Banco Mundial/FMI suelen ser anuales).
- Aunque no requieran key, la mayoría tiene límites de frecuencia de consulta razonable — evita loops de solicitudes masivas en una sola sesión.
- Distingue siempre, al presentar resultados, si el dato viene de una fuente oficial (sección 1-2 y 4) o de una librería no oficial (sección 3) — esto es relevante si el entregable se comparte fuera del equipo interno.
- Si el dato más preciso solo está disponible detrás de una API con token (ej. series largas de Banxico SIE o INEGI Indicadores), dilo explícitamente en vez de aproximar con el canal de descarga directa sin avisar.

## Fuentes excluidas por requerir API key (para referencia futura)

INEGI (API Indicadores/BIE), Banxico (SIE API), UN Comtrade, FRED (Fed de EE.UU.), Alpha Vantage. Si en algún momento el área correspondiente gestiona esos tokens de forma centralizada (no por usuario individual), se pueden agregar como sección adicional de esta skill.
