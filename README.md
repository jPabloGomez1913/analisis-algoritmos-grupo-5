### Laboratorio #4: Programación dinámica y algoritmos voraces
# 1. Presentación
## Caso #2: Plataforma Pulso - programación de las jornadas de las unidades móviles

### Integrantes:
- Juliana Arroyave Arango
- Juliana Gómez Legarda
- Juan Pablo Gómez
- Felipe Londoño García

Grupo: 190304006-3

Profesor: Santiago Suárez Cortés

# 2. Análisis del problema
## Descripción general del problema
La Secretaría de Salud cuenta con nueve unidades móviles de valoración, una asignada a cada subregión del departamento. Mensualmente, los municipios presentan solicitudes para realizar jornadas de atención, indicando la fecha y hora de inicio, la fecha y hora de finalización (incluyendo el tiempo de desplazamiento) y la cantidad de pacientes de alto riesgo que tienen pendientes de atención.

El problema surge porque cada unidad móvil solamente puede atender una jornada a la vez. Por lo tanto, cuando dos o más solicitudes presentan horarios superpuestos, es necesario decidir cuáles serán aceptadas y cuáles deberán rechazarse.

Actualmente, el coordinador realiza esta asignación siguiendo el orden de llegada de las solicitudes. Este procedimiento acepta una jornada cuando no presenta conflictos con las jornadas previamente programadas. Sin embargo, esta estrategia no garantiza que se obtenga la mayor cantidad posible de jornadas durante el mes, puesto que una solicitud aceptada inicialmente puede impedir la programación de varias jornadas posteriores.

Para resolver el problema, se propone implementar un algoritmo voraz que seleccione las jornadas según su hora de finalización, priorizando aquellas que terminan más temprano. Después de seleccionar una jornada, el algoritmo evalúa las solicitudes restantes y acepta únicamente aquellas cuyo horario de inicio sea mayor o igual a la hora de finalización de la última jornada seleccionada. El algoritmo se ejecutará independientemente para cada subregión, debido a que cada una dispone de su propia unidad móvil.

Es importante aclarar que el criterio de optimización elegido es **maximizar el número de jornadas**, no maximizar la cantidad de pacientes de alto riesgo atendidos. Por esta razón, el número de pacientes pendientes se conserva como información de cada solicitud, pero no interviene en la decisión de selección.
## Entradas, salidas, restricciones y supuestos de la operación
### Entradas
- Entre 40 y 120 solicitudes mensuales por subregión.
- Fecha y hora de inicio de cada jornada.
- Fecha y hora de finalización de cada jornada, incluido el desplazamiento.
- Cantidad de pacientes de alto riesgo pendientes por municipio.
- Identificación del municipio y de la subregión.
### Salidas
- Lista de jornadas seleccionadas.
- Cantidad total de jornadas programadas.
- Información de identificación, horario y municipio de cada jornada seleccionada.
### Restricciones
- Cada subregión cuenta con una única unidad móvil.
- No puede existir ninguna superposición de horarios para una misma unidad.
- El tiempo de desplazamiento se incluye dentro de la duración de cada jornada.
- Maximización de la cantidad de jornadas.
- Ejecución secuencial en un servidor de aproximadamente 380 W.
### Supuestos de la operación
- Una solicitud puede iniciar inmediatamente después de la hora de finalización de la solicitud anterior (es decir, el intervalo se entiende como `[inicio, finalización)`)
- Todos los datos ingresados son válidos y consistentes.
- Los datos son inmutables durante la ejecución.
- La solución no incluye una interfaz gráfica.
- Ausencia de persistencia en bases de datos.
- Carga completa de datos en memoria.
- Utilización de conjuntos de datos sintéticos de tamaño creciente.
- Ejecución en un único hilo y servidor.
# 3. Diseño de la solución
## ¿Por qué el problema admite la estrategia elegida?
La Operación 3 de la plataforma Pulso admite una estrategia voraz porque corresponde al problema clásico de selección de actividades, cuyo objetivo es seleccionar el mayor número posible de intervalos compatibles entre sí.

En este caso, cada actividad representa una solicitud de jornada de valoración de una unidad móvil. Cada solicitud tiene una hora de inicio y una hora de finalización. La estrategia elegida consiste en seleccionar siempre la jornada que termina más temprano entre las solicitudes disponibles, ya que esta decisión permite liberar la unidad móvil lo antes posible y dejar la mayor cantidad de tiempo disponible para programar otras jornadas.
## Ejemplo práctico resuelto paso a paso:
Para representar el funcionamiento del algoritmo, supongamos que una unidad móvil de valoración de una subregión recibe las siguientes seis solicitudes de jornadas durante el mes:
| Jornada | Hora de inicio | Hora de finalización |
| ------- | -------------- | -------------------- |
| 1       | 08:00          | 10:00                |
| 2       | 09:00          | 11:00                |
| 3       | 10:00          | 12:00                |
| 4       | 11:00          | 13:00                |
| 5       | 12:00          | 14:00                |
| 6       | 13:00          | 15:00                |

### Paso 1: Ordenar las solicitudes por hora de finalización
En este ejemplo, las solicitudes ya se encuentran ordenadas de menor a mayor hora de finalización:

`[1, 2, 3, 4, 5, 6]`
### Paso 2: Selecccionar la primera actividad
Se selecciona la primera activdad del paso anterior, es decir, la que tiene menor hora de finalización:

`Jornada 1 (08:00 - 10:00)`
### Paso 3: Evaluar la siguiente jornada (jornada 2)
Se evalúa la siguiente jornada por orden de hora de finalización, es decir, la jornada 2:

`Jornada 2 (09:00 - 11:00)`

Como se traslapa su hora de inicio con la hora de finalización de la jornada 1, entonces la jornada 2 es **rechazada**.
### Paso 4: Evaluar la jornada 3
Se evalúa la siguiente jornada por orden de hora de finalización, es decir, la jornada 3:

`Jornada 3 (10:00 - 12:00)`

Como **NO** se traslapa su hora de inicio con la hora de finalización de la jornada 1, entonces la jornada 3 es **aceptada**.
### Paso 5: Evaluar la jornada 4
Se evalúa la jornada 4:

`Jornada 4 (11:00 - 13:00)`

Como se traslapa su hora de inicio con la hora de finalización de la jornada 3, entonces la jornada 4 es **rechazada**.
### Paso 6: Evaluar la jornada 5
Se evalúa la jornada 5:

`Jornada 5 (12:00 - 14:00)`

Como **NO** se traslapa su hora de inicio con la hora de finalización de la jornada 3, entonces la jornada 5 es **aceptada**.
### Paso 7: Evaluar la jornada 6
Se evalúa la jornada 6:

`Jornada 6 (13:00 - 15:00)`

Como se traslapa su hora de inicio con la hora de finalización de la jornada 5, entonces la jornada 6 es **rechazada**.
### Paso 8: Condensación de la solución
Se consolidan las jornadas aceptadas en un único listado, se excluyen entonces las jornadas rechazadas del arreglo original. De esta manera queda entonces la siguiente lista de solicitudes ordenada por hora de finalización:

`Jornadas [1, 3, 5]`

El total de solicitudes aceptadas para el mes es de **3**.

# 4. Implementación

## Descripción de la solución desarrollada

El código se encuentra en `src/jornadas_unidades/`. Cada archivo tiene una función específica dentro del desarrollo del proyecto:

- [estrategia.py](src/jornadas_unidades/estrategia.py): contiene la estrategia voraz (`seleccionar_jornadas`) y las funciones de apoyo `hay_cruce` y `valor`.
- [exhaustivo.py](src/jornadas_unidades/exhaustivo.py): contiene una solución que prueba todas las combinaciones posibles de solicitudes (2ⁿ). Se utiliza como referencia para comprobar si los resultados son óptimos en casos pequeños.
- [regla_actual.py](src/jornadas_unidades/regla_actual.py): representa la forma en que el coordinador realiza actualmente la asignación, teniendo en cuenta el orden de llegada de las solicitudes y rechazando aquellas que se cruzan.
- [datos.py](src/jornadas_unidades/datos.py): genera ejemplos de solicitudes de manera automática, utilizando una semilla fija para obtener los mismos datos en cada ejecución.
- [medicion.py](src/jornadas_unidades/medicion.py): compara el tiempo y la cantidad de operaciones de las tres soluciones con diferentes cantidades de solicitudes. También guarda los resultados en archivos CSV y genera las gráficas.
- [pruebas.py](src/jornadas_unidades/pruebas.py): contiene pruebas con `assert` para comprobar que las tres soluciones funcionen correctamente.

## Tecnologías y herramientas utilizadas

- Python 3.12.5, utilizando anotaciones de tipo y docstrings para facilitar la comprensión del código.
- Biblioteca estándar: `csv`, `gc`, `math`, `random`, `statistics`, `time`, `functools`, `pathlib` y `typing`.
- Librerías externas: `matplotlib` para crear las gráficas y `numpy` para calcular el exponente empírico a partir de los resultados. Las versiones exactas están en `requirements.txt`.
- GitHub para trabajar en equipo y llevar un registro de los cambios realizados en el proyecto.

## Decisiones de implementación relevantes

- **Jornadas que se tocan en un extremo.** Se estableció que una jornada puede comenzar justo cuando termina otra, sin que esto se considere un cruce. Para manejar esta situación, los intervalos se representan como `[inicio, fin)`. Por esta razón, la estrategia voraz utiliza `>=` y la función `hay_cruce` utiliza `>` para identificar los cruces. La regla actual también sigue esta misma condición, de manera que las tres soluciones trabajen bajo las mismas reglas.

- **Ordenamiento estable y empates.** Cuando dos solicitudes terminan a la misma hora, Python mantiene el orden en el que fueron recibidas. De esta forma, se selecciona primero la que llegó antes. Esto no afecta la cantidad de jornadas que se pueden asignar, ya que ambas solicitudes liberan la unidad al mismo tiempo, pero permite obtener resultados consistentes en cada ejecución.

- **Tres soluciones escritas a mano.** Se decidió desarrollar las tres soluciones sin utilizar librerías especializadas en intervalos u optimización. Así es posible entender cómo funciona cada una, revisar sus pasos y contar las operaciones que realiza, facilitando una comparación más clara entre ellas. Para ordenar las solicitudes se utiliza la función `sorted` de Python, en lugar de implementar un algoritmo de ordenamiento propio.

- **Datos sintéticos reproducibles.** La función `generar_instancia` utiliza un generador propio (`random.Random(semilla)`) para crear las solicitudes. Esto permite que, al utilizar la misma cantidad de solicitudes (`n`) y la misma semilla, se obtengan siempre los mismos datos. De esta manera, las tres soluciones trabajan con exactamente la misma información. Además, las solicitudes se entregan en el orden en que fueron generadas, que es el que necesita la regla actual.

- **Horizonte que crece con n.** El tiempo disponible para las jornadas se calcula con la fórmula `n · 180` minutos. Esto se hace porque, si el tiempo disponible fuera siempre el mismo, al aumentar la cantidad de solicitudes sería más probable que todas se cruzaran. Al aumentar también el tiempo disponible, se mantiene una proporción similar entre las solicitudes y el tiempo, lo que permite comparar mejor los resultados. Las duraciones de las jornadas van de 1 a 8 horas y los pacientes de alto riesgo se asignan aleatoriamente entre 1 y 40, aunque este dato no influye en la selección de las jornadas.

- **Contadores separados de las funciones medidas.** En `medicion.py`, las funciones `contar_voraz`, `contar_regla_actual` y `contar_exhaustivo` permiten conocer cuántas operaciones realiza cada solución. Para hacerlo, repiten la lógica de las estrategias y llevan un registro de las operaciones sin modificar las funciones originales. Esto permite medir el tiempo de ejecución de las soluciones por separado, sin que el conteo afecte los resultados. En cada prueba también se comprueba que los contadores produzcan el mismo resultado que las funciones originales.

- **Cómo se cronometra.** Para medir el tiempo de ejecución se utiliza `time.perf_counter` y se realizan varias repeticiones, tomando como resultado la mediana de los tiempos obtenidos. Esto ayuda a evitar que situaciones momentáneas del sistema alteren demasiado las mediciones. Además, se desactiva el recolector de basura durante las pruebas y no se incluye el tiempo que tarda en generarse la información.

- **Verificación dentro del experimento.** En `medicion.py` se realizan comprobaciones durante cada prueba para verificar que las jornadas seleccionadas no se crucen, que la regla actual no obtenga un resultado mejor que la estrategia voraz y que la voraz coincida con la solución exhaustiva cuando ambas se ejecutan con el mismo tamaño de solicitudes. Por el alto costo de procesamiento de esta última, solo se realizan mediciones hasta `n = 20`.

- **Qué cubren las pruebas.** En `pruebas.py` se comprueba el funcionamiento de las soluciones en diferentes situaciones: cuando no hay solicitudes, cuando solo hay una, cuando ninguna se cruza y cuando todas se cruzan. También se revisa el comportamiento de `hay_cruce` en los extremos de los intervalos `[inicio, fin)`, el ejemplo de seis jornadas presentado en la sección 3 y 30 instancias aleatorias. En estas últimas se verifica que la estrategia voraz coincida con la exhaustiva, que no existan cruces y que la regla actual no supere el resultado de la voraz. Finalmente, se incluye un contraejemplo en el que la regla actual acepta 1 jornada, mientras que la estrategia voraz permite seleccionar 4.

# 5. Evaluación del desempeño

# 6. Análisis comparativo
## Un contraejemplo calculado
Se supone que una unidad móvil recibe las siguientes cinco solicitudes. La columna orden de llegada indica el orden en que fueron recibidas las solicitudes.
| Orden de llegada | Solicitud | Inicio | Finalización |
| ---------------- | --------- | ------ | ------------ |
| 1                | A         | 08:00  | 16:00        |
| 2                | B         | 08:00  | 10:00        |
| 3                | C         | 10:00  | 12:00        |
| 4                | D         | 12:00  | 14:00        |
| 5                | E         | 14:00  | 16:00        |
### Escenario actual
Después de que la organización procese las solicitudes en el orden en que fueron recibidas:
1. Solicitud A: se acepta porque no existen jornadas previamente programadas. Ocupa el intervalo de `08:00 a 16:00`.
2. Solicitud B: se **rechaza** porque se traslapa con la jornada A.
3. Solicitud C: se **rechaza** porque se traslapa con la jornada A.
4. Solicitud D: se **rechaza** porque se traslapa con la jornada A.
5. Solicitud E: se **rechaza** porque se traslapa con la jornada A.

De esta manera, la organización termina programando únicamente la jornada A, aunque existen otras solicitudes que podrían haberse atendido de manera consecutiva.
### Escenario óptimo
Para maximizar el número de jornadas, se seleccionan las solicitudes compatibles que permiten aprovechar mejor el tiempo disponible. Se escoge inicialmente la solicitud con fecha de finalización más pronta, y se seleccionan posteriormente las solicitudes que tengas la fecha de finalización más pronto a la fecha de inicio de la última solicitud aceptada. En la tabla a continuación, se muestran las solicitudes ordenadas por fecha de finalización:
| Orden de llegada | Solicitud | Inicio | Finalización |
| ---------------- | --------- | ------ | ------------ |
| 2                | B         | 08:00  | 10:00        |
| 3                | C         | 10:00  | 12:00        |
| 4                | D         | 12:00  | 14:00        |
| 1                | A         | 08:00  | 16:00        |
| 5                | E         | 14:00  | 16:00        |

1. Solicitud B: se **acepta** porque no existen jornadas previamente programadas. Ocupa el intervalo de `08:00 a 10:00`.
2. Solicitud C: se **acepta** porque su fecha de finalización es mayor o igual a la fecha de inicio de la solicitud previamente aceptada. Ocupa el intervalo de `10:00 a 12:00`.
3. Solicitud D: se **acepta**. Ocupa el intervalo de `12:00 a 14:00`.
4. Solicitud A: se **rechaza** porque su fecha de inicio es menor a la fecha de finalización de la solicitud previamente aceptada `08:00 < 14:00`.
5. Solicitud E: se **acepta**. Ocupa el intervalo de `14:00 a 16:00`.

Esta solución óptima acepta entonces las solicitudes [B, C, D y E], un total de `4 `solicitudes aceptadas; `3` más comparadas con las solicutes que hubieran sido aceptadas en usando el escenario actual.
## La condición contraria
Actualmente, todas las jornadas tienen el mismo valor para el algoritmo: cada jornada aceptada aporta una unidad al objetivo, independientemente de cuántos pacientes de alto riesgo tenga pendientes el municipio.

Si la organización cambia su prioridad y decide que las jornadas deben seleccionarse según la cantidad de pacientes de alto riesgo que podrían atender, el problema se convierte en una variante conocida como selección ponderada de actividades.

En este escenario:
- Cada solicitud tendría un peso asociado al número de pacientes de alto riesgo pendientes.
- El objetivo sería maximizar la suma de pacientes asociados a las jornadas seleccionadas.
- Se mantendría la restricción de que una unidad móvil no puede atender dos jornadas simultáneamente.
- Una jornada que termina primero ya no sería necesariamente la mejor elección, porque podría atender a pocos pacientes frente a otra jornada más extensa que beneficie a muchos más.

La elección entre una estrategia voraz y una estrategia de programación dinámica depende del objetivo que se pretenda optimizar. Si se busca maximizar el número de jornadas, se recomienda la estrategia voraz de menor hora de finalización. Si se busca maximizar la cantidad de pacientes de alto riesgo atendidos, se recomienda la programación dinámica para selección ponderada de intervalos.
## Recomendación

# 7. Implicaciones éticas, sociales y ambientales

# 8. Conclusiones (pendiente...)

# 9. Instrucciones para reproducir el experimento

## ¿Cómo preparar el entorno para correr los programas?
1. Inicie el entorno virtual, ejecute los siguientes comandos en CMD:
    - `python -m venv venv` para crear el entorno virtual
    - `venv\Scripts\activate` para iniciar el entorno en Windows
    - `source venv/bin/activate` para iniciar el entorno en Linux/Mac

2. Instale las librerías del archivo de requerimientos en caso de no tenerlas instaladas. Ejecute en la terminal `pip install -r requirements.txt`