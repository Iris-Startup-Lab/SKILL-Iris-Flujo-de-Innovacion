# Matriz de Ambición Estratégica × Palancas — How Might We

Referencia vinculante para la sección de encuadre estratégico. El catálogo oficial es el nodo
«Ambición estratégica» de `pasos.json`; esta matriz es su copia para trabajar la skill sola. Si
los dos no coinciden, manda `pasos.json`.

## Ambición estratégica y sus palancas

| Ambición estratégica | Palancas disponibles |
|---|---|
| **Optimizar Negocio Actual** | Reducir Costos · Productividad |
| **Crecer Negocio Actual** | Nuevos Clientes · Mayor Frecuencia · Mayor Ticket · Recuperación · Participación de Mercado |
| **Expandir Negocio** | Ampliar Mercado · Nuevos Casos de Uso · Ecosistema |
| **Crear Nuevos Negocios** | Nuevo Producto · Nuevo Modelo de Negocio |
| **Reinventar el Futuro** | Disrupción · Nuevas Categorías · Inteligencia artificial |

## Reglas de uso

1. La pregunta 1 (ambición) y la pregunta 2 (palanca) son **cerradas**: se muestran las 5
   ambiciones completas, con su texto y en su orden, y después solo las palancas de la elegida.
2. **Nunca quites, renombres, fusiones ni reordenes** las opciones. Mostrar 3 ambiciones «porque
   las otras no aplican» es decidir por el usuario.
3. **Sí puedes añadir** una ambición propia al final —el nodo lo permite (`permite_propuestas`)—
   con tres condiciones: va después de las oficiales, marcada como «propuesta mía, no forma parte
   del catálogo original», y con una línea que explique por qué encaja en este proyecto. Si el
   usuario la elige, se registra con `--forzar` y queda anotada como propuesta.
4. Si el usuario responde una palanca de **otra** ambición, no la aceptes: vuelve a presentar las
   de la suya. Eso no es una propuesta, es un cruce de ramas.
5. **No mostrar las palancas de otras ambiciones**; solo las correspondientes a la ambición
   elegida. Son 17 en total y mostrarlas juntas convierte una decisión en un catálogo.
6. Cada How Might We generado debe ser coherente con la ambición y la palanca seleccionadas.

## Palancas que hay que explicar al presentarlas

Siete no se entienden solas. Explícalas cuando las muestres, sin esperar a que el usuario
pregunte (mismo texto que el `glosario` del nodo en `pasos.json`):

| Palanca | Qué significa |
| --- | --- |
| Recuperación | Volver a activar clientes que te compraban y dejaron de hacerlo. |
| Participación de Mercado | Ganar terreno a la competencia dentro del mismo mercado, sin agrandarlo. |
| Ecosistema | Dejar de vender solo tu producto y montar una plataforma donde otros —proveedores, socios, desarrolladores, incluso competidores— ofrezcan lo suyo junto a lo tuyo. Tú ganas por facilitar esos intercambios: comisión, suscripción o el valor de los datos que se generan. |
| Nuevos Casos de Uso | Usar lo que ya tienes para resolver un problema distinto, con la misma capacidad. |
| Disrupción | Atacar el mercado con una propuesta más simple o más barata que la actual, aunque canibalice lo que ya vendes. |
| Nuevas Categorías | Crear un tipo de producto que hoy no existe y que todavía no tiene nombre en el mercado. |
| Inteligencia artificial | Usar inteligencia artificial como el motor del negocio, no como un adorno. |

**«Inteligencia artificial» exige cuatro respuestas.** Nunca la aceptes como etiqueta. Al
elegirla, pregunta y deja por escrito: qué decisión concreta automatiza o mejora, con qué datos se
alimenta, qué pasa cuando se equivoca y por qué esa capacidad es difícil de copiar. Si alguna
queda sin respuesta, la palanca real es otra —productividad, nuevo producto, reducir costos— con
una etiqueta de moda encima, y conviene decirlo.

## Formato de How Might We

- Usar siempre "¿Cómo podríamos...?".
- Cada How Might We debe referenciar el insight o dato que lo origina (Insight base).
- Nivel de amplitud: amplio / intermedio / específico (default intermedio).
