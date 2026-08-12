# Fórmulas de Tamaño de Muestra — Discovery Survey

Referencia vinculante para `scripts/calcular_muestra.py` y para la sección de cálculo de muestra de la Testing Card.

## 1. Tamaño de muestra (población infinita o muy grande)

```
n = (Z² × p × (1 − p)) / e²
```

## 2. Tamaño de muestra ajustado por población finita

```
n_aj = n / (1 + (n − 1) / N)
```

## 3. Envíos requeridos (considerando tasa de respuesta)

```
envíos = n_aj / tasa_respuesta
```

## Variables

| Símbolo | Significado | Valor típico |
|---|---|---|
| **Z** | Valor Z según nivel de confianza | 1.96 (95%) |
| **p** | Proporción estimada | 0.5 si no se conoce (caso más conservador) |
| **e** | Margen de error aceptable (proporción) | 0.05 |
| **N** | Tamaño de la población total `{{N}}` | según contexto |
| **n** | Muestra para población infinita | calculado |
| **n_aj** | Muestra ajustada al tamaño real | calculado |

## Valores Z por nivel de confianza

| Nivel de confianza | Z |
|---|---|
| 80% | 1.28 |
| 85% | 1.44 |
| 90% | 1.64 |
| **95%** | **1.96** |
| 98% | 2.33 |
| 99% | 2.58 |

## Tasas de respuesta orientativas (para sugerir si el usuario no sabe)

| Canal | Tasa de respuesta típica |
|---|---|
| Panel pagado | 30 – 60% |
| Base de clientes propia / email interno | 20 – 40% |
| Email frío / lista comprada | 2 – 10% |
| Intercept / en sitio | 5 – 15% |
| Redes sociales orgánicas | 1 – 5% |

## Nota de integridad

Los valores de `N`, `tasa_respuesta`, `confianza` y `error` los confirma el agente con el usuario; si no se conocen, se sugieren supuestos razonados marcados con `*`. Las cifras resultantes son deterministas (calculadas por el script), no estimaciones del modelo.
