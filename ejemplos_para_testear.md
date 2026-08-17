# Guía de Pruebas y Casos de Uso del Flujo de Innovación IRIS

Este documento proporciona **3 ejemplos completos y diferenciados** para probar el funcionamiento end-to-end del flujo de innovación IRIS (`iris-flujo-de-innovacion`). Cada ejemplo cubre una casuística metodológica distinta, detallando:
- Ficha de contexto de negocio e hipótesis iniciales.
- Tipo de ruta y justificación estratégica.
- Secuencia paso a paso con comandos CLI reproducibles (`scripts/estado_flujo.py` y `generar_html.py`).
- Decisiones exactas (según [pasos.json](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/pasos.json)).
- Sub-skills invocadas, datos heredados y criterios de verificación.

---

## Entorno Previo de Ejecución

Antes de ejecutar los comandos en PowerShell, activa el entorno virtual de Anaconda:

```powershell
& "E:\Users\1167486\AppData\Local\anaconda3\Scripts\conda.exe" shell.powershell hook | Out-String | Invoke-Expression
conda activate skills_env
```

---

## Tabla Comparativa de los 3 Ejemplos

| Parámetro | Ejemplo 1: Salud & FoodTech | Ejemplo 2: FinTech & B2B SaaS | Ejemplo 3: DeepTech & Circular Economy |
| :--- | :--- | :--- | :--- |
| **Proyecto** | `NutriSmart MX` | `CobranzaIA B2B` | `EcoPack Circular` |
| **Tipo de Ruta** | **Ruta Completa** (11 pasos) | **Ruta Mínima Express** (5 pasos) | **Ruta Exploratoria / Híbrida** (con omisiones y pivote) |
| **Punto de Partida** | Estado actual (`benchmark-mercado`) | Opiniones / Foros (`discussion-forums` + `search-trend-analysis`) | Futuros / Prospectiva (`foresight`) |
| **Evidencia de Campo** | Datos reales (Entrevistas + Kano + Day in the life) | Supuestos calculados (*) (Omisión formal) | Simulación de insights (`SIMULADO` + Expo Quest) |
| **Enfoque de Ideación** | Nuevo producto + Referral Builder | Optimización / Productividad | Reinventar el Futuro / IA + Caressing client |
| **Validación Final** | `landing-page` + `online-ads` | `feature-stub` + `email-campaign` | `explainer-video` + `popup-store` |

---

## Ejemplo 1: Ruta Completa (End-to-End) — NutriSmart MX

### 1. Ficha del Proyecto
- **Nombre:** `NutriSmart MX`
- **Objetivo:** Validar la demanda de un servicio de suscripción de planes nutricionales hiperpersonalizados con entrega de comidas funcionales listas para calentar.
- **Audiencia:** Profesionales urbanos de 28 a 45 años en CDMX y Monterrey con jornadas laborales intensas y metas de salud específicas.
- **Ruta seleccionada:** `completa` (11 pasos sin omisiones).

---

### 2. Ejecución Paso a Paso

#### Paso 0: Inicialización
```bash
python scripts/estado_flujo.py init --proyecto "NutriSmart MX" \
    --objetivo "Validar demanda de suscripción de comida funcional hiperpersonalizada" \
    --audiencia "Profesionales urbanos 28-45 años CDMX y MTY"
```

---

#### Paso 1: `html_1` — Inicio + Investigación
1. **Inspección del paso:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_1
   python scripts/estado_flujo.py iniciar --paso html_1
   ```
2. **Registro de decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_1 \
       --nodo "¿Cómo quieres iniciar?" --opcion "Estado actual"
   ```
3. **Sub-skill invocada:** [1.Investigacion/benchmark-mercado](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/1.Investigacion/benchmark-mercado/AGENTE.md)
   - *Insumos:* Mercado de meal kits y healthy delivery en México (TAM/SAM/SOM, competidores directos e indirectos, ticket promedio $120–$180 MXN).
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_1.json --estado flujo_estado.json --paso html_1 -o html_1.html
   python scripts/estado_flujo.py completar --paso html_1 \
       --skills 1.Investigacion/benchmark-mercado \
       --resumen "TAM MX $8.4B MXN; competidores enfocados en dietas genéricas sin personalización clínica" \
       --veredicto perseverar --outputs html_1.html --datos reporte_html_1.json
   ```

---

#### Paso 2: `html_2` — Decisión Entrevistas
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_2
   python scripts/estado_flujo.py iniciar --paso html_2
   ```
2. **Decisiones:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_2 \
       --nodo "¿Ejecución de entrevistas?" --opcion "Sí — respuestas e insights reales"
   python scripts/estado_flujo.py decision --paso html_2 \
       --nodo "Selección de agentes" --opcion "A Day In The Life"
   python scripts/estado_flujo.py decision --paso html_2 \
       --nodo "Selección de agentes" --opcion "Encuesta Kano"
   ```
3. **Sub-skill invocada:** [2.Descubrimiento/entrevistas-empatia](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/entrevistas-empatia/AGENTE.md)
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_2.json --estado flujo_estado.json --paso html_2 -o html_2.html
   python scripts/estado_flujo.py completar --paso html_2 \
       --skills 2.Descubrimiento/entrevistas-empatia \
       --resumen "15 entrevistas reales: 80% abandona dietas por tiempo de preparación y falta de variedad" \
       --veredicto perseverar --outputs html_2.html --datos reporte_html_2.json
   ```

---

#### Paso 3: `html_3` — Descubrimiento (Paralelo)
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_3
   python scripts/estado_flujo.py iniciar --paso html_3
   ```
2. **Sub-skills invocadas en paralelo:**
   - [2.Descubrimiento/day-in-the-life](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/day-in-the-life/AGENTE.md)
   - [2.Descubrimiento/encuesta-kano](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/encuesta-kano/AGENTE.md)
3. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_3.json --estado flujo_estado.json --paso html_3 -o html_3.html
   python scripts/estado_flujo.py completar --paso html_3 \
       --skills "2.Descubrimiento/day-in-the-life,2.Descubrimiento/encuesta-kano" \
       --resumen "Kano identifica como Atractivo la personalización según analítica de sangre; Must-be entrega puntual" \
       --veredicto perseverar --outputs html_3.html --datos reporte_html_3.json
   ```

---

#### Paso 4: `html_4` — Persona Profile
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_4
   python scripts/estado_flujo.py iniciar --paso html_4
   ```
2. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_4 \
       --nodo "¿Hay datos reales de entrevistas / encuestas?" --opcion "Sí — generación de profiles con data real"
   ```
3. **Sub-skill invocada:** [2.Descubrimiento/persona-profile](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/persona-profile/AGENTE.md)
   - *Protopersona resultante:* "Rodrigo — Ejecutivo Senior Enfocado en Longevidad" (JTBD: Mantener energía constante y control de glucosa sin cocinar).
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_4.json --estado flujo_estado.json --paso html_4 -o html_4.html
   python scripts/estado_flujo.py completar --paso html_4 \
       --skills 2.Descubrimiento/persona-profile \
       --resumen "Perfil Rodrigo definido con datos reales de 15 entrevistas y Kano" \
       --veredicto perseverar --outputs html_4.html --datos reporte_html_4.json
   ```

---

#### Paso 5: `html_5` — Problem-Solution Fit
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_5
   python scripts/estado_flujo.py iniciar --paso html_5
   ```
2. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_5 \
       --nodo "Elección de protopersona" --opcion "Por problema más grande"
   ```
3. **Sub-skill invocada:** [2.Descubrimiento/problem-solution-fit](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/problem-solution-fit/AGENTE.md)
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_5.json --estado flujo_estado.json --paso html_5 -o html_5.html
   python scripts/estado_flujo.py completar --paso html_5 \
       --skills 2.Descubrimiento/problem-solution-fit \
       --resumen "Dolor crítico: Frustración por preparar viandas sanas domingo por la noche (Score dolor 9/10)" \
       --veredicto perseverar --outputs html_5.html --datos reporte_html_5.json
   ```

---

#### Paso 6: `html_6` — Journey Builder
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_6
   python scripts/estado_flujo.py iniciar --paso html_6
   ```
2. **Sub-skill invocada:** [2.Descubrimiento/journey-builder](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/journey-builder/AGENTE.md)
   - Mapeo de 10 pasos con fricción mayor en "Paso 4: Planificación de compras semanales" y "Paso 7: Conservación de alimentos".
3. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_6.json --estado flujo_estado.json --paso html_6 -o html_6.html
   python scripts/estado_flujo.py completar --paso html_6 \
       --skills 2.Descubrimiento/journey-builder \
       --resumen "Puntos críticos identificados en selección y conservación semanal de ingredientes" \
       --veredicto perseverar --outputs html_6.html --datos reporte_html_6.json
   ```

---

#### Paso 7: `html_7` — HMW + Ambición Estratégica
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_7
   python scripts/estado_flujo.py iniciar --paso html_7
   ```
2. **Decisiones:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Ambición estratégica" --opcion "Crear Nuevos Negocios"
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Apalancamiento" --opcion "Nuevo modelo de negocio"
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Selección de agentes de ideación" --opcion "Ideación"
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Selección de agentes de ideación" --opcion "Referral Builder"
   ```
3. **Sub-skill invocada:** [3.Ideacion/how-might-we](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/how-might-we/AGENTE.md)
   - *HMW central:* "¿Cómo podríamos garantizar a Rodrigo una alimentación funcional personalizada sin que dedique más de 5 minutos a la semana a planear y cocinar?"
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_7.json --estado flujo_estado.json --paso html_7 -o html_7.html
   python scripts/estado_flujo.py completar --paso html_7 \
       --skills 3.Ideacion/how-might-we \
       --resumen "HMW formulado bajo ambición Crear Nuevos Negocios con palanca Nuevo modelo de negocio" \
       --veredicto perseverar --outputs html_7.html --datos reporte_html_7.json
   ```

---

#### Paso 8: `html_8` — Ideación
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_8
   python scripts/estado_flujo.py iniciar --paso html_8
   ```
2. **Sub-skills invocadas en paralelo:**
   - [3.Ideacion/ideacion](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/ideacion/AGENTE.md)
   - [3.Ideacion/referral-builder](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/referral-builder/AGENTE.md)
3. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_8 \
       --nodo "Selección de ideas" --opcion "Suscripción Smart Chef: Menú quincenal con escaneo de biomarkers y comidas al vacío listas en 3 min"
   ```
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_8.json --estado flujo_estado.json --paso html_8 -o html_8.html
   python scripts/estado_flujo.py completar --paso html_8 \
       --skills "3.Ideacion/ideacion,3.Ideacion/referral-builder" \
       --resumen "12 ideas generadas; seleccionada Suscripción Smart Chef con incentivo de referidos corporativos" \
       --veredicto perseverar --outputs html_8.html --datos reporte_html_8.json
   ```

---

#### Paso 9: `html_9` — Dimensionador Estratégico
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_9
   python scripts/estado_flujo.py iniciar --paso html_9
   ```
2. **Sub-skill invocada:** [3.Ideacion/dimensionador-estrategico](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/dimensionador-estrategico/AGENTE.md)
   - Evaluación económica: SOM proyectado año 1 = $18.5M MXN (1,200 suscriptores recurrentes).
3. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_9.json --estado flujo_estado.json --paso html_9 -o html_9.html
   python scripts/estado_flujo.py completar --paso html_9 \
       --skills 3.Ideacion/dimensionador-estrategico \
       --resumen "Score de atractivo 8.7/10; SOM año 1 estimado en $18.5M MXN con margen bruto de 42%" \
       --veredicto perseverar --outputs html_9.html --datos reporte_html_9.json
   ```

---

#### Paso 10: `html_10` — Business Model Navigator
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_10
   python scripts/estado_flujo.py iniciar --paso html_10
   ```
2. **Sub-skill invocada:** [3.Ideacion/business-model-navigator](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/business-model-navigator/AGENTE.md)
   - Patrón recomendado: *Subscription + Direct-to-Consumer + Mass Customization*.
3. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_10.json --estado flujo_estado.json --paso html_10 -o html_10.html
   python scripts/estado_flujo.py completar --paso html_10 \
       --skills 3.Ideacion/business-model-navigator \
       --resumen "Patrón Subscription + Mass Customization recomendado para validar con Landing Page y Ads" \
       --veredicto perseverar --outputs html_10.html --datos reporte_html_10.json
   ```

---

#### Paso 11: `html_11` — Prototipado y Validación
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_11
   python scripts/estado_flujo.py iniciar --paso html_11
   ```
2. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_11 \
       --nodo "Selección de agente para validar" --opcion "Simple Landing Page"
   python scripts/estado_flujo.py decision --paso html_11 \
       --nodo "Selección de agente para validar" --opcion "Online Ads"
   ```
3. **Sub-skills invocadas en paralelo:**
   - [4.Prototipado/landing-page](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/4.Prototipado/landing-page/AGENTE.md)
   - [5.Validacion/online-ads](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/5.Validacion/online-ads/AGENTE.md)
4. **Generación de HTML y Cierre del Flujo:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_11.json --estado flujo_estado.json --paso html_11 -o html_11.html
   python scripts/estado_flujo.py completar --paso html_11 \
       --skills "4.Prototipado/landing-page,5.Validacion/online-ads" \
       --resumen "Experimento diseñado: Landing page con checkout simulado + campaña Meta Ads con testing card" \
       --veredicto perseverar --outputs html_11.html --datos reporte_html_11.json
   ```

---

## Ejemplo 2: Ruta Mínima Express — CobranzaIA B2B

### 1. Ficha del Proyecto
- **Nombre:** `CobranzaIA B2B`
- **Objetivo:** Validar un agente de IA generativa que automatiza la conciliación bancaria y la cobranza preventiva para PyMEs en México vía WhatsApp y correo.
- **Audiencia:** Directores de Finanzas y dueños de PyMEs B2B con facturación entre $10M y $50M MXN anuales.
- **Ruta seleccionada:** `minima` (`html_1 → html_4 → html_7 → html_8 → html_11`). Los pasos no esenciales quedan omitidos por diseño.

---

### 2. Ejecución Paso a Paso

#### Paso 0: Inicialización en Modo Ruta Mínima
```bash
python scripts/estado_flujo.py init --proyecto "CobranzaIA B2B" \
    --objetivo "Validar agente de IA para cobranza preventiva y conciliación en PyMEs" \
    --audiencia "Directores de Finanzas y Dueños de PyMEs B2B México" \
    --ruta minima
```
*Resultado:* Los pasos `html_2`, `html_3`, `html_5`, `html_6`, `html_9` y `html_10` quedan marcados como `omitido` de entrada con su impacto declarado.

---

#### Paso 1: `html_1` — Inicio + Investigación (Cadena de Foros)
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_1
   python scripts/estado_flujo.py iniciar --paso html_1
   ```
2. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_1 \
       --nodo "¿Cómo quieres iniciar?" --opcion "Opiniones y comentarios"
   ```
3. **Sub-skills invocadas en cadena:**
   - [1.Investigacion/discussion-forums](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/1.Investigacion/discussion-forums/AGENTE.md)
   - [1.Investigacion/search-trend-analysis](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/1.Investigacion/search-trend-analysis/AGENTE.md)
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_1.json --estado flujo_estado.json --paso html_1 -o html_1.html
   python scripts/estado_flujo.py completar --paso html_1 \
       --skills "1.Investigacion/discussion-forums,1.Investigacion/search-trend-analysis" \
       --resumen "Tendencia creciente en búsquedas de 'automatizar cobranza CFDI'; fricción recurrente en conciliación SAT vs Bancos" \
       --veredicto perseverar --outputs html_1.html --datos reporte_html_1.json
   ```

---

#### Paso 4: `html_4` — Persona Profile (Generación con Supuestos)
*Nota:* Al provenir de `html_2` y `html_3` omitidos, el nodo condicional de `pasos.json` activa automáticamente la rama de supuestos.
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_4
   python scripts/estado_flujo.py iniciar --paso html_4
   ```
2. **Decisión registrada:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_4 \
       --nodo "¿Hay datos reales de entrevistas / encuestas?" --opcion "No — generación de profiles a base de supuestos"
   ```
3. **Sub-skill invocada:** [2.Descubrimiento/persona-profile](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/persona-profile/AGENTE.md)
   - *Persona construida:* "Mariana — Gerente de Finanzas PyME" (Atributos marcados con `*` por ausencia de entrevistas de campo).
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_4.json --estado flujo_estado.json --paso html_4 -o html_4.html
   python scripts/estado_flujo.py completar --paso html_4 \
       --skills 2.Descubrimiento/persona-profile \
       --resumen "Protopersona Mariana formulada a base de supuestos de industria*; dolor principal: 15h/semana en reclamo manual" \
       --veredicto perseverar --outputs html_4.html --datos reporte_html_4.json
   ```

---

#### Paso 7: `html_7` — HMW + Ambición Estratégica
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_7
   python scripts/estado_flujo.py iniciar --paso html_7
   ```
2. **Decisiones:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Ambición estratégica" --opcion "Optimizar Negocio Actual"
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Apalancamiento" --opcion "Productividad"
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Selección de agentes de ideación" --opcion "Ideación"
   ```
3. **Sub-skill invocada:** [3.Ideacion/how-might-we](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/how-might-we/AGENTE.md)
   - *HMW formulado:* "¿Cómo podríamos reducir en un 80% el tiempo manual que Mariana dedica a la cobranza sin deteriorar la relación comercial con sus clientes?"
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_7.json --estado flujo_estado.json --paso html_7 -o html_7.html
   python scripts/estado_flujo.py completar --paso html_7 \
       --skills 3.Ideacion/how-might-we \
       --resumen "HMW enfocado en Productividad para Mariana (PyMEs B2B)" \
       --veredicto perseverar --outputs html_7.html --datos reporte_html_7.json
   ```

---

#### Paso 8: `html_8` — Ideación
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_8
   python scripts/estado_flujo.py iniciar --paso html_8
   ```
2. **Sub-skill invocada:** [3.Ideacion/ideacion](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/ideacion/AGENTE.md)
3. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_8 \
       --nodo "Selección de ideas" --opcion "Bot de cobranza empático conectado al ERP con recordatorios automatizados por WhatsApp"
   ```
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_8.json --estado flujo_estado.json --paso html_8 -o html_8.html
   python scripts/estado_flujo.py completar --paso html_8 \
       --skills 3.Ideacion/ideacion \
       --resumen "Idea seleccionada: Bot conciliador y cobranza vía WhatsApp con integración API" \
       --veredicto perseverar --outputs html_8.html --datos reporte_html_8.json
   ```

---

#### Paso 11: `html_11` — Prototipado y Validación (Validación en Producto / Outbound)
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_11
   python scripts/estado_flujo.py iniciar --paso html_11
   ```
2. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_11 \
       --nodo "Selección de agente para validar" --opcion "Feature Stub"
   python scripts/estado_flujo.py decision --paso html_11 \
       --nodo "Selección de agente para validar" --opcion "Email Campaign"
   ```
3. **Sub-skills invocadas en paralelo:**
   - [5.Validacion/feature-stub](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/5.Validacion/feature-stub/AGENTE.md)
   - [5.Validacion/email-campaign](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/5.Validacion/email-campaign/AGENTE.md)
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_11.json --estado flujo_estado.json --paso html_11 -o html_11.html
   python scripts/estado_flujo.py completar --paso html_11 \
       --skills "5.Validacion/feature-stub,5.Validacion/email-campaign" \
       --resumen "Experimentos diseñados: Botón falso (Feature Stub) en portal contable partner + Campaña Outbound de 500 emails fríos" \
       --veredicto perseverar --outputs html_11.html --datos reporte_html_11.json
   ```

---

## Ejemplo 3: Ruta Exploratoria / Híbrida — EcoPack Circular

### 1. Ficha del Proyecto
- **Nombre:** `EcoPack Circular`
- **Objetivo:** Explorar y prototipar envases bio-basados solubles en agua a partir de residuos agroindustriales (bagazo de agave) para la industria de cosméticos y e-commerce.
- **Audiencia:** Marcas de cosmética natural D2C y operadores logísticos de última milla en Latinoamérica.
- **Ruta seleccionada:** `completa` con omisiones selectivas justificadas en descubrimiento e ideación.

---

### 2. Ejecución Paso a Paso

#### Paso 0: Inicialización
```bash
python scripts/estado_flujo.py init --proyecto "EcoPack Circular" \
    --objetivo "Explorar y validar envases bio-basados solubles para cosmética D2C" \
    --audiencia "Marcas de cosmética natural D2C y operadores logísticos LatAm"
```

---

#### Paso 1: `html_1` — Inicio con Futuros y Prospectiva
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_1
   python scripts/estado_flujo.py iniciar --paso html_1
   ```
2. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_1 \
       --nodo "¿Cómo quieres iniciar?" --opcion "Futuros"
   ```
3. **Sub-skill invocada:** [1.Investigacion/foresight](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/1.Investigacion/foresight/AGENTE.md)
   - Escenarios 2028–2035: Regulación estricta de plásticos de un solo uso e impuestos al carbono en empaques.
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_1.json --estado flujo_estado.json --paso html_1 -o html_1.html
   python scripts/estado_flujo.py completar --paso html_1 \
       --skills 1.Investigacion/foresight \
       --resumen "Megatendencias regulatorias acelerarán demanda de biomateriales solubles un 35% CAGR al 2030" \
       --veredicto perseverar --outputs html_1.html --datos reporte_html_1.json
   ```

---

#### Paso 2: `html_2` — Entrevistas Simuladas y Descubrimiento Presencial
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_2
   python scripts/estado_flujo.py iniciar --paso html_2
   ```
2. **Decisiones (Rama No real → Simular respuestas):**
   ```bash
   python scripts/estado_flujo.py decision --paso html_2 \
       --nodo "¿Ejecución de entrevistas?" --opcion "No — simulación de respuestas e insights"
   python scripts/estado_flujo.py decision --paso html_2 \
       --nodo "Simular o no" --opcion "Simular respuestas"
   python scripts/estado_flujo.py decision --paso html_2 \
       --nodo "Selección de agentes" --opcion "Expo Quest"
   ```
3. **Sub-skill invocada:** [2.Descubrimiento/entrevistas-empatia](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/entrevistas-empatia/AGENTE.md)
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_2.json --estado flujo_estado.json --paso html_2 -o html_2.html
   python scripts/estado_flujo.py completar --paso html_2 \
       --skills 2.Descubrimiento/entrevistas-empatia \
       --resumen "Guion de entrevista estructurado e insights sintéticos SIMULADO generados" \
       --veredicto perseverar --outputs html_2.html --datos reporte_html_2.json
   ```

---

#### Paso 3: `html_3` — Descubrimiento en Ferias y Expos
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_3
   python scripts/estado_flujo.py iniciar --paso html_3
   ```
2. **Sub-skill invocada:** [2.Descubrimiento/expo-quest](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/expo-quest/AGENTE.md)
   - Mapeo de eventos objetivo: *Expo Pack México*, *Green Tech Summit Guadalajara*.
3. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_3.json --estado flujo_estado.json --paso html_3 -o html_3.html
   python scripts/estado_flujo.py completar --paso html_3 \
       --skills 2.Descubrimiento/expo-quest \
       --resumen "3 eventos clave identificados para testear prototipos físicos de empaque ante directores de compras" \
       --veredicto perseverar --outputs html_3.html --datos reporte_html_3.json
   ```

---

#### Paso 4: `html_4` — Persona Profile
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_4
   python scripts/estado_flujo.py iniciar --paso html_4
   ```
2. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_4 \
       --nodo "¿Hay datos reales de entrevistas / encuestas?" --opcion "No — generación de profiles a base de supuestos"
   ```
3. **Sub-skill invocada:** [2.Descubrimiento/persona-profile](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/persona-profile/AGENTE.md)
   - *Persona:* "Camila — Fundadora de Marca D2C Sustentable" (Etiquetada como `SUPUESTOS / SIMULADO*`).
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_4.json --estado flujo_estado.json --paso html_4 -o html_4.html
   python scripts/estado_flujo.py completar --paso html_4 \
       --skills 2.Descubrimiento/persona-profile \
       --resumen "Perfil Camila (D2C Cosmética) generado con supuestos SIMULADO*" \
       --veredicto perseverar --outputs html_4.html --datos reporte_html_4.json
   ```

---

#### Paso 5: `html_5` — Problem-Solution Fit
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_5
   python scripts/estado_flujo.py iniciar --paso html_5
   ```
2. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_5 \
       --nodo "Elección de protopersona" --opcion "Por mayor tamaño en mercado"
   ```
3. **Sub-skill invocada:** [2.Descubrimiento/problem-solution-fit](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/2.Descubrimiento/problem-solution-fit/AGENTE.md)
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_5.json --estado flujo_estado.json --paso html_5 -o html_5.html
   python scripts/estado_flujo.py completar --paso html_5 \
       --skills 2.Descubrimiento/problem-solution-fit \
       --resumen "Fit validado en costo de empaque sustentable vs resistencia a humedad durante traslados" \
       --veredicto perseverar --outputs html_5.html --datos reporte_html_5.json
   ```

---

#### Paso 6: `html_6` — Omisión Selectiva de Journey Builder
El equipo decide omitir el mapeo detallado del viaje para avanzar directamente a la ideación:
```bash
python scripts/estado_flujo.py omitir --paso html_6 \
    --motivo "Enfoque en material y viabilidad técnica; no se requiere mapeo de puntos de contacto de usuario en esta fase"
```
*Impacto registrado:* El HMW de `html_7` no contará con el anclaje a obstáculos de interacción detallados.

---

#### Paso 7: `html_7` — HMW + Ambición Disruptiva
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_7
   python scripts/estado_flujo.py iniciar --paso html_7
   ```
2. **Decisiones:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Ambición estratégica" --opcion "Reinventar el Futuro"
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Apalancamiento" --opcion "Disrupción"
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Selección de agentes de ideación" --opcion "Ideación"
   python scripts/estado_flujo.py decision --paso html_7 \
       --nodo "Selección de agentes de ideación" --opcion "Caressing the client"
   ```
3. **Sub-skill invocada:** [3.Ideacion/how-might-we](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/how-might-we/AGENTE.md)
   - *HMW formulado:* "¿Cómo podríamos crear empaques para cosméticos que desaparezcan instantáneamente al contacto con agua tibia sin comprometer la protección del producto durante el envío?"
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_7.json --estado flujo_estado.json --paso html_7 -o html_7.html
   python scripts/estado_flujo.py completar --paso html_7 \
       --skills 3.Ideacion/how-might-we \
       --resumen "Reto disruptivo enfocado en empaques hidrosolubles compostables" \
       --veredicto perseverar --outputs html_7.html --datos reporte_html_7.json
   ```

---

#### Paso 8: `html_8` — Ideación
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_8
   python scripts/estado_flujo.py iniciar --paso html_8
   ```
2. **Sub-skills invocadas en paralelo:**
   - [3.Ideacion/ideacion](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/ideacion/AGENTE.md)
   - [3.Ideacion/caressing-client](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/caressing-client/AGENTE.md)
3. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_8 \
       --nodo "Selección de ideas" --opcion "Cápsulas de envío 'DissolvPack' con sellado térmico y disolución en regadera con aroma herbal"
   ```
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_8.json --estado flujo_estado.json --paso html_8 -o html_8.html
   python scripts/estado_flujo.py completar --paso html_8 \
       --skills "3.Ideacion/ideacion,3.Ideacion/caressing-client" \
       --resumen "Idea seleccionada: DissolvPack, empaque hidrosoluble aromático para cosmética" \
       --veredicto perseverar --outputs html_8.html --datos reporte_html_8.json
   ```

---

#### Paso 9: `html_9` — Dimensionador Estratégico
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_9
   python scripts/estado_flujo.py iniciar --paso html_9
   ```
2. **Sub-skill invocada:** [3.Ideacion/dimensionador-estrategico](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/3.Ideacion/dimensionador-estrategico/AGENTE.md)
3. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_9.json --estado flujo_estado.json --paso html_9 -o html_9.html
   python scripts/estado_flujo.py completar --paso html_9 \
       --skills 3.Ideacion/dimensionador-estrategico \
       --resumen "TAM regional $1.2B USD; requerimiento de inversión en moldes de $15,000 USD para prototipo" \
       --veredicto perseverar --outputs html_9.html --datos reporte_html_9.json
   ```

---

#### Paso 10: `html_10` — Omisión de Business Model Navigator
```bash
python scripts/estado_flujo.py omitir --paso html_10 \
    --motivo "Modelo B2B industrial estándar de venta por millar; no se requiere exploración de nuevos patrones de monetización"
```

---

#### Paso 11: `html_11` — Validación con Video Explicativo y Pop-Up Store
1. **Inspección e inicio:**
   ```bash
   python scripts/estado_flujo.py mostrar --paso html_11
   python scripts/estado_flujo.py iniciar --paso html_11
   ```
2. **Decisión:**
   ```bash
   python scripts/estado_flujo.py decision --paso html_11 \
       --nodo "Selección de agente para validar" --opcion "Explainer Video"
   python scripts/estado_flujo.py decision --paso html_11 \
       --nodo "Selección de agente para validar" --opcion "Pop-Up Store"
   ```
3. **Sub-skills invocadas en paralelo:**
   - [5.Validacion/explainer-video](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/5.Validacion/explainer-video/AGENTE.md)
   - [5.Validacion/popup-store](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/sub-skills/5.Validacion/popup-store/AGENTE.md)
4. **Generación de HTML y Cierre:**
   ```bash
   python _plantilla_html/scripts/generar_html.py --data reporte_html_11.json --estado flujo_estado.json --paso html_11 -o html_11.html
   python scripts/estado_flujo.py completar --paso html_11 \
       --skills "5.Validacion/explainer-video,5.Validacion/popup-store" \
       --resumen "Diseño de Testing Card: Video demo en LinkedIn Ads + Stand de prueba física en Expo Pack Guadalajara" \
       --veredicto perseverar --outputs html_11.html --datos reporte_html_11.json
   ```

---

## Lista de Verificación y Criterios de Éxito al Testear

Al correr cualquiera de los tres ejemplos anteriores, verifica los siguientes puntos clave del sistema:

1. **Persistencia del Estado:**
   - Cada llamada a `scripts/estado_flujo.py` debe actualizar de inmediato [flujo_estado.json](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/flujo_estado.json) y regenerar [STATE.md](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/STATE.md).
2. **Contrato de Herencia de Datos:**
   - Al cerrar un paso con `--datos <reporte.json>`, el paso siguiente hereda la estructura en su bloque `flujo.ruta[].datos`.
   - Si un paso fue omitido, los pasos dependientes deben registrar la etiqueta `*` o `[SUPUESTO / SIMULADO]` en sus variables y advertencias.
3. **Consistencia de HTMLs:**
   - Los archivos `.html` resultantes se abren directamente en el navegador y contienen el riel de navegación interactivo de 11 pasos, la paleta corporativa IRIS (morado y dorado) y el logo oficial embebido en base64 sin enlaces rotos.
4. **Integridad de Decisiones:**
   - Los nodos de decisión no permiten opciones inventadas; deben coincidir de forma estricta con las opciones estipuladas en [pasos.json](file:///e:/Users/1167486/Local/scripts/skills_generales/macro_skill_flujo_de_innovacion_iris/pasos.json).
