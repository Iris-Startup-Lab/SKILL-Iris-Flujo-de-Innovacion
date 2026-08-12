# Benchmarks de Industria — Search Trend Analysis

Rangos de referencia para calibrar el **umbral de éxito** y la interpretación de los datos de tendencias de búsqueda. Los valores son **rangos orientativos de la industria** (fuentes públicas: WordStream, Backlinko, HubSpot, informes SEO). **No son datos exactos por cuenta**: el agente debe complementar con `webfetch` y marcarlos como `[REFERENCIA DE INDUSTRIA]` cuando se citen.

## 1. Orden de magnitud de volúmenes de búsqueda (Google, mensual, aprox.)

| Segmento | Búsquedas mensuales (MX / ES) | Búsquedas mensuales (global) |
|---|---|---|
| Long-tail / nicho emergente | 10 – 1,000 | 100 – 10,000 |
| Nicho medio | 1,000 – 10,000 | 10,000 – 100,000 |
| Categoría popular | 10,000 – 100,000 | 100,000 – 1,000,000 |
| Categoría masiva (head) | 100,000+ | 1,000,000+ |

> Regla práctica: una keyword con < 100 búsquedas/mes en México rara vez sostiene una señal de demanda por sí sola; en global, el umbral equivalente suele ser 1,000/mes.

## 2. Tasas de crecimiento de búsqueda (12 meses)

| Señal | Interpretación |
|---|---|
| Crecimiento > 25% anual | Tendencia emergente fuerte (señal positiva). |
| 15 – 25% anual | Crecimiento sostenido (señal positiva moderada). |
| 0 – 15% anual | Demanda estable; validar con otras señales. |
| Decrecimiento | Demanda en contracción (señal negativa). |

## 3. Métricas de campaña de referencia (para contrastar, si el usuario las necesita)

| Métrica | Rango típico |
|---|---|
| CTR búsqueda (Google Ads, media) | 2 – 5% |
| CPC búsqueda (ES/MX, media) | USD 0.30 – 1.50 (varía fuerte por industria) |
| CPC búsqueda (industrias competitivas: seguros, legal, fintech) | USD 2 – 20+ |
| CPL (costo por lead, B2B MX) | USD 5 – 40 |

## 4. Ajuste por idioma y mercado

- **Español (México / LATAM):** volúmenes menores que inglés; umbrales de "señal positiva" deben escalar a la baja (ej. ~10% del equivalente inglés).
- **Inglés (global/US):** mayor volumen y competencia; usar umbrales más altos.
- El **umbral de éxito por mercado** (`{{umbral_exito}}`) siempre se fija relativo al tamaño del país/idioma, nunca absoluto.

## 5. Cómo usar esta referencia

1. El script `google_trends.py` entrega interés **relativo 0-100**, no volumen absoluto.
2. Para estimar volumen absoluto, se cruza el interés relativo con los rangos de la sección 1 y, si es posible, con benchmarks públicos obtenidos por `webfetch`.
3. Toda cifra estimada se marca con `*` y se cita la fuente o el rango usado de esta tabla.
