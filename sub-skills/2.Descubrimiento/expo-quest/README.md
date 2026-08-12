# expo-quest

> Fase: 2.Descubrimiento

Encuentra eventos presenciales reales (expos, ferias, conferencias, meetups) en México —priorizando CDMX— donde interactuar con un perfil objetivo o estudiar a la competencia, verificando fecha/ubicación/costo en sitios oficiales. Usar cuando el usuario quiera encontrar eventos, ferias o expos para hacer investigación de mercado, customer journey o contacto directo con su público.

## Salida principal — HTML interactivo

Esta skill entrega su resultado como un **reporte HTML autocontenido** con el diseño corporativo IRIS (logo oficial + paleta morado/dorado, tipografías Sora/Inter).

### Generar el HTML

1. Estructura el resultado en `reporte.json` (esquema `REPORT_DATA` de `_plantilla_html/README.md`).
2. Ejecuta:
   ```bash
   python ../../../_plantilla_html/scripts/generar_html.py --data reporte.json -o reporte.html
   ```
3. Entrega `reporte.html`.

El logo oficial (`assets/logo.png`) se embebe automáticamente en base64. Diseño de referencia: `Designs_files/Design_iris_main_colors.md`.
