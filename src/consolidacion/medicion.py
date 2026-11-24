"""Medición experimental de las estrategias de consolidación de pacientes.

Mide el tiempo de las dos estrategias de estrategias.py (tabla hash y lista
enlazada simple). En cada tamaño, ambas reciben las mismas instancias y el
propio experimento verifica que devuelven exactamente el mismo resultado.
Los tiempos se guardan en CSV y se generan las gráficas.
"""

import math
import time
from pathlib import Path
import matplotlib.pyplot as plt

from datos import generar_resultados
from estrategias import consolidar_con_lista_enlazada, consolidar_con_tabla_hash
from modelo import Resultado

Fila = dict[str, str | int | float]

# Raíz del repositorio: este archivo está en <raíz>/src/consolidacion/.
RAIZ = Path(__file__).resolve().parents[2]
ruta_resultados = RAIZ / "resultados" / "consolidacion"
ruta_graficas = RAIZ / "graficas" / "consolidacion"

TAMANOS = [50, 100, 500, 1000, 5000, 10000]

ESTRATEGIAS = {
    "tabla_hash": consolidar_con_tabla_hash,
    "lista_enlazada": consolidar_con_lista_enlazada,
}

NOMBRES: dict[str, str] = {
    "tabla_hash": "Tabla hash",
    "lista_enlazada": "Lista enlazada simple",
}

# Complejidad teórica del tiempo (p ≈ n pacientes distintos).
ETIQUETAS_COMPLEJIDAD: dict[str, str] = {
    "tabla_hash": "O(n)",
    "lista_enlazada": "O(n²)",
}

ESTILOS: dict[str, tuple[str, str]] = {
    "tabla_hash": ("#1f77b4", "o"),
    "lista_enlazada": ("#d62728", "s"),
}

REPETICIONES = 5
SEMILLAS = (11, 23, 37)

def mediana(valores: list[float]) -> float:
    """Calcula la mediana de una lista de números.

    Args:
        valores: números a resumir.

    Returns:
        El valor central de la lista ordenada (o el promedio de los dos
        centrales si la cantidad es par).
    """
    ordenados = sorted(valores)
    mitad = len(ordenados) // 2
    if len(ordenados) % 2 == 1:
        return ordenados[mitad]
    return (ordenados[mitad - 1] + ordenados[mitad]) / 2


def promedio(valores: list[float]) -> float:
    """Calcula el promedio aritmético de una lista de números.

    Args:
        valores: números a promediar.

    Returns:
        La suma de los valores dividida entre la cantidad.
    """
    return sum(valores) / len(valores)


def complejidad_teorica(nombre: str, n: int) -> float:
    """Evalúa la función de complejidad teórica f(n) de una estrategia.

    Args:
        nombre: clave de la estrategia en ESTRATEGIAS.
        n: tamaño de la entrada.

    Returns:
        n para la tabla hash, O(n); n² para la lista enlazada, O(n²).
    """
    return float(n) if nombre == "tabla_hash" else float(n * n)

def medir_tiempo(
    nombre: str, instancia: list[Resultado], repeticiones: int
) -> tuple[float, list[Resultado]]:
    """Mide el tiempo de una estrategia sobre una instancia.

    Ejecuta la estrategia varias veces con time.perf_counter y devuelve la
    mediana, menos sensible que el promedio a interrupciones del sistema
    operativo. Solo se cronometra la ejecución, nunca la generación de los
    datos.

    Args:
        nombre: clave de la estrategia en ESTRATEGIAS.
        instancia: resultados de entrada (no se modifican).
        repeticiones: número de ejecuciones a medir.

    Returns:
        Tupla (mediana del tiempo en segundos, resultado de la última corrida).
    """
    estrategia = ESTRATEGIAS[nombre]
    tiempos: list[float] = []
    resultado: list[Resultado] = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        resultado = estrategia(instancia)
        tiempos.append(time.perf_counter() - inicio)
    return mediana(tiempos), resultado


def repeticiones_para(n: int) -> int:
    """Define cuántas repeticiones se miden según el tamaño.

    Los tamaños grandes tardan varios segundos con la lista enlazada, así
    que se repiten menos veces.

    Args:
        n: tamaño de la instancia.

    Returns:
        Número de repeticiones de la medición.
    """
    return 3 if n >= 10_000 else REPETICIONES


def medir_experimento() -> list[Fila]:
    """Ejecuta el experimento completo sobre todos los tamaños.

    Para cada tamaño se genera una instancia por semilla; ambas estrategias
    reciben la misma instancia y se verifica que coinciden exactamente
    (mismos resultados, en el mismo orden).

    Returns:
        Una fila por estrategia y tamaño con el tiempo (mediana entre
        semillas) y el número promedio de pacientes consolidados.
    """
    filas: list[Fila] = []
    print("Midiendo...")
    for n in TAMANOS:
        tiempos: dict[str, list[float]] = {nombre: [] for nombre in ESTRATEGIAS}
        pacientes: list[float] = []
        for semilla in SEMILLAS:
            instancia = generar_resultados(n, semilla)  # la misma para ambas
            salidas: dict[str, list[Resultado]] = {}
            for nombre in ESTRATEGIAS:
                tiempo, salida = medir_tiempo(nombre, instancia, repeticiones_para(n))
                tiempos[nombre].append(tiempo)
                salidas[nombre] = salida
            assert salidas["tabla_hash"] == salidas["lista_enlazada"], (n, semilla)
            pacientes.append(len(salidas["tabla_hash"]))
        for nombre in ESTRATEGIAS:
            fila: Fila = {
                "estrategia": nombre,
                "n": n,
                "tiempo_s": mediana(tiempos[nombre]),
                "pacientes_consolidados": round(promedio(pacientes)),
            }
            filas.append(fila)
            print(f"  {nombre:<15} n={n:>6}  {fila['tiempo_s']:.6f} s")
    return filas

def extraer(filas: list[Fila], nombre: str) -> tuple[list[int], list[float]]:
    """Extrae los tamaños y tiempos medidos de una estrategia.

    Args:
        filas: resultados de la medición.
        nombre: estrategia a extraer.

    Returns:
        Tupla (tamaños, tiempos) en el orden medido.
    """
    seleccion = [f for f in filas if f["estrategia"] == nombre]
    return [int(f["n"]) for f in seleccion], [float(f["tiempo_s"]) for f in seleccion]

def contrastar(filas: list[Fila]) -> list[Fila]:
    """Contrasta lo medido con la complejidad teórica.

    Calcula la constante empírica c = t / f(n), con f la complejidad
    teórica. Si la complejidad es correcta, c se mantiene aproximadamente
    estable al crecer n. También calcula el factor de crecimiento del tiempo
    respecto al tamaño anterior y el que predice la teoría.

    Args:
        filas: resultados de la medición.

    Returns:
        Una fila por medición con la constante y los factores de crecimiento.
    """
    contraste: list[Fila] = []
    for nombre in ESTRATEGIAS:
        tamanos, tiempos = extraer(filas, nombre)
        for i, (n, t) in enumerate(zip(tamanos, tiempos)):
            fila: Fila = {
                "estrategia": nombre,
                "n": n,
                "tiempo_s": t,
                "complejidad": ETIQUETAS_COMPLEJIDAD[nombre],
                "constante_c": t / complejidad_teorica(nombre, n),
                "factor_observado": "",
                "factor_esperado": "",
            }
            if i > 0:
                anterior = tamanos[i - 1]
                fila["factor_observado"] = round(t / tiempos[i - 1], 2)
                fila["factor_esperado"] = round(
                    complejidad_teorica(nombre, n) / complejidad_teorica(nombre, anterior), 2
                )
            contraste.append(fila)
    return contraste

def guardar_csv(filas: list[Fila], ruta: Path) -> None:
    """Guarda las filas de resultados en un archivo CSV separado por comas.

    La primera línea tiene los nombres de las columnas y cada fila siguiente
    sus valores. Ningún valor contiene comas, así que no hace falta citarlos.

    Args:
        filas: filas a guardar (todas con las mismas columnas).
        ruta: archivo de destino.
    """
    ruta.parent.mkdir(parents=True, exist_ok=True)
    columnas = list(filas[0].keys())
    lineas = [",".join(columnas)]
    for fila in filas:
        lineas.append(",".join(str(fila[columna]) for columna in columnas))
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def graficar_comparacion(filas: list[Fila], ruta: Path) -> None:
    """Grafica el tiempo de ambas estrategias contra n en dos escalas.

    A la izquierda, ejes lineales: se ve la forma de cada curva (recta para
    la tabla hash, parábola para la lista enlazada). A la derecha, ejes
    log-log: la pendiente de cada recta es el exponente del crecimiento.

    Args:
        filas: resultados de la medición.
        ruta: imagen de destino.
    """
    fig, (lineal, loglog) = plt.subplots(1, 2, figsize=(13, 5.5))
    for nombre, (color, marca) in ESTILOS.items():
        tamanos, tiempos = extraer(filas, nombre)
        etiqueta = f"{NOMBRES[nombre]} (teórica {ETIQUETAS_COMPLEJIDAD[nombre]})"
        for eje in (lineal, loglog):
            eje.plot(tamanos, tiempos, marker=marca, color=color, label=etiqueta)
    lineal.set_title("Escala lineal")
    loglog.set_title("Escala log-log")
    loglog.set_xscale("log")
    loglog.set_yscale("log")
    for eje in (lineal, loglog):
        eje.set_xlabel("Número de resultados (n)")
        eje.set_ylabel("Tiempo de ejecución (s, mediana)")
        eje.grid(True, which="both", alpha=0.3)
        eje.legend()
    fig.suptitle("Consolidación de pacientes: tiempo vs. tamaño de entrada")
    fig.tight_layout()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=150)
    plt.close(fig)

def graficar_teorica(filas: list[Fila], nombre: str, ruta: Path) -> None:
    """Superpone los tiempos medidos de una estrategia con su curva teórica.

    La curva teórica c · f(n) se escala con la constante del tamaño mayor
    medido, para comparar la forma del crecimiento.

    Args:
        filas: resultados de la medición.
        nombre: estrategia a graficar.
        ruta: imagen de destino.
    """
    tamanos, tiempos = extraer(filas, nombre)
    etiqueta = ETIQUETAS_COMPLEJIDAD[nombre]
    c = tiempos[-1] / complejidad_teorica(nombre, tamanos[-1])
    teorica = [c * complejidad_teorica(nombre, n) for n in tamanos]
    color, marca = ESTILOS[nombre]
    fig, eje = plt.subplots(figsize=(8, 5))
    eje.plot(tamanos, tiempos, marker=marca, color=color, label="Medido")
    eje.plot(tamanos, teorica, "--", color="gray", label=f"Teórico c · {etiqueta}")
    eje.set_xscale("log")
    eje.set_yscale("log")
    eje.set_xlabel("Número de resultados (n)")
    eje.set_ylabel("Tiempo (s, mediana)")
    eje.set_title(f"{NOMBRES[nombre]}: medido vs. {etiqueta}")
    eje.grid(True, which="both", alpha=0.3)
    eje.legend()
    fig.tight_layout()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def main() -> None:
    """Ejecuta el experimento completo y guarda tablas y gráficas."""
    filas = medir_experimento()
    contraste = contrastar(filas)

    guardar_csv(filas, ruta_resultados / "tiempos.csv")
    guardar_csv(contraste, ruta_resultados / "contraste_complejidad.csv")

    graficar_comparacion(filas, ruta_graficas / "tiempo_vs_n.png")
    for nombre in ESTRATEGIAS:
        graficar_teorica(filas, nombre, ruta_graficas / f"{nombre}_teorica.png")

    print("\nFactor de crecimiento respecto al tamaño anterior (observado vs. esperado):")
    for fila in contraste:
        if fila["factor_observado"] != "":
            print(
                f"  {fila['estrategia']:<15} n={fila['n']:>6}"
                f"  x{fila['factor_observado']:<8} (esp. x{fila['factor_esperado']})"
            )

    print(f"\nResultados en {ruta_resultados}")
    print(f"Graficas en {ruta_graficas}")


if __name__ == "__main__":
    main()