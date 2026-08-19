# encuesta-kano

> Fase: 2.Descubrimiento

Genera una encuesta modelo Kano para evaluar el valor percibido y la deseabilidad de cada feature de una propuesta de valor, y clasifica las respuestas (funcional x disfuncional) en categorías M/O/A/I/R/Q. Usar cuando el usuario quiera crear una encuesta Kano, evaluar la deseabilidad de características/funcionalidades de un producto, o clasificar respuestas Kano.

## Salida principal — HTML interactivo

Esta skill entrega su resultado como un **reporte HTML autocontenido** con el diseño corporativo IRIS (logo oficial + paleta morado/dorado, tipografías Sora/Inter).

### Generar el HTML

1. Estructura el resultado en `reporte.json` (esquema `REPORT_DATA` de `_plantilla_html/README.md`).
2. Ejecuta **desde la raíz del repositorio**:

   ```bash
   # como paso del flujo: el contexto del flujo se inyecta solo
   python _plantilla_html/scripts/generar_html.py --data reporte.json \
       --estado flujo_estado.json --paso html_N -o html_N.html

   # skill suelta
   python _plantilla_html/scripts/generar_html.py --data reporte.json --sin-flujo -o reporte.html
   ```

3. Entrega el HTML.

El logo se embebe en base64: el oficial del repositorio, o la copia `assets/logo.png` de
esta carpeta si la skill corre fuera del repo. Diseño de referencia:
`Designs_files/Design_iris_main_colors.md`.

## Simulación (sub-skill)

`simulador/` contiene un **simulador de respuestas** para cuando no hay a quién encuestar:
genera `kano_respuestas_SIMULADO.csv` con las columnas exactas que consume
`scripts/clasificar_kano.py`, con muestreo reproducible por semilla, intervalos de Wilson y
coeficientes de Berger. El análisis posterior es el mismo que con respuestas reales.

```bash
python simulador/scripts/simular_kano.py plan.json -o kano_respuestas_SIMULADO.csv
python scripts/clasificar_kano.py kano_respuestas_SIMULADO.csv -o clasificacion_SIMULADO.csv
```

Instrucciones: `simulador/SIMULADOR.md`. Convención: `sub-skills/SIMULACION.md`.

## Uso independiente

Esta skill es un paso del flujo IRIS, pero no depende de él para funcionar. Para usarla
sola basta con esta carpeta más `_plantilla_html/` al lado, y ejecutar el generador con
`--sin-flujo`: el contexto del flujo se omite y el logo sale de `assets/logo.png`.

Lo que aporta el repositorio completo —y que se pierde al extraerla— es el contexto del
flujo en el HTML (riel de progreso, decisiones previas, pasos omitidos) y el histórico de
`flujo_estado.json`. Nada de eso es necesario para producir el entregable.
