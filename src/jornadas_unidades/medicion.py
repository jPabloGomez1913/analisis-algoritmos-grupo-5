"""Medición experimental del desempeño de las estrategias de jornadas.

Mide el tiempo de ejecución de las tres soluciones (voraz, regla actual por
orden de llegada y exhaustiva) sobre instancias sintéticas de tamaño
creciente, guarda los resultados en CSV, genera las gráficas y contrasta el
crecimiento observado con la complejidad teórica de cada estrategia.

Uso (desde src/jornadas_unidades):
    python medicion.py
"""

import csv
import math
import statistics
import time
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")  # genera las imágenes sin abrir ventanas
import matplotlib.pyplot as plt
import numpy as np

from datos import generar_instancia
from estrategia import Jornada, seleccionar_jornadas
from exhaustivo import seleccionar_exhaustivo
from regla_actual import asignar_por_llegada

Estrategia = Callable[[list[Jornada]], list[Jornada]]

RAIZ = Path(__file__).resolve().parents[2]
CARPETA_RESULTADOS = RAIZ / "resultados"
CARPETA_GRAFICAS = RAIZ / "graficas"

ESTRATEGIAS: dict[str, Estrategia] = {
    "voraz": seleccionar_jornadas,
    "regla_actual": asignar_por_llegada,
    "exhaustivo": seleccionar_exhaustivo,
}

# Tamaños de entrada por estrategia. El rango real del caso (40 a 120
# solicitudes por subregión) está incluido; los tamaños mayores permiten ver
# la tendencia asintótica. La exhaustiva solo es viable con n pequeño.
TAMANOS: dict[str, list[int]] = {
    "voraz": [40, 80, 120, 250, 500, 1_000, 2_000, 4_000, 8_000, 16_000, 32_000, 64_000],
    "regla_actual": [40, 80, 120, 250, 500, 1_000, 2_000, 4_000, 8_000, 16_000],
    "exhaustivo": [4, 6, 8, 10, 12, 14, 16, 18],
}

# Complejidad teórica de cada estrategia, como función de n.
COMPLEJIDAD: dict[str, tuple[str, Callable[[int], float]]] = {
    "voraz": ("O(n log n)", lambda n: n * math.log2(n)),
    "regla_actual": ("O(n²)", lambda n: float(n * n)),
    "exhaustivo": ("O(2ⁿ · n)", lambda n: (2.0**n) * n),
}

REPETICIONES = 5
SEMILLAS = (11, 23, 37)


def medir_tiempo(estrategia: Estrategia, instancia: list[Jornada], repeticiones: int) -> float:
    """Mide el tiempo de una estrategia sobre una instancia.

    Ejecuta la estrategia varias veces con time.perf_counter y devuelve la
    mediana, que es menos sensible que el promedio a interrupciones del
    sistema operativo.

    Args:
        estrategia: función que recibe las solicitudes y devuelve las jornadas.
        instancia: solicitudes de entrada (no se modifican).
        repeticiones: número de ejecuciones a medir.

    Returns:
        Mediana del tiempo de ejecución, en segundos.
    """
    tiempos: list[float] = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        estrategia(instancia)
        tiempos.append(time.perf_counter() - inicio)
    return statistics.median(tiempos)


def medir_estrategia(nombre: str, tamanos: list[int]) -> list[dict[str, float | int | str]]:
    """Mide una estrategia en todos sus tamaños de entrada.

    Para cada tamaño se generan varias instancias (una por semilla) y se
    reporta la mediana de sus tiempos, junto con las jornadas elegidas.

    Args:
        nombre: clave de la estrategia en ESTRATEGIAS.
        tamanos: tamaños de entrada a medir.

    Returns:
        Una fila por tamaño con estrategia, n, tiempo (s) y jornadas elegidas.
    """
    estrategia = ESTRATEGIAS[nombre]
    filas: list[dict[str, float | int | str]] = []
    for n in tamanos:
        repeticiones = 1 if nombre == "exhaustivo" and n >= 16 else REPETICIONES
        tiempos: list[float] = []
        jornadas: list[int] = []
        for semilla in SEMILLAS:
            instancia = generar_instancia(n, semilla)
            tiempos.append(medir_tiempo(estrategia, instancia, repeticiones))
            jornadas.append(len(estrategia(instancia)))
        filas.append(
            {
                "estrategia": nombre,
                "n": n,
                "tiempo_s": statistics.median(tiempos),
                "jornadas_elegidas": round(statistics.mean(jornadas), 1),
            }
        )
        print(f"  {nombre:<13} n={n:>6}  {filas[-1]['tiempo_s']:.6f} s")
    return filas


def guardar_csv(filas: list[dict[str, float | int | str]], ruta: Path) -> None:
    """Guarda las filas de resultados en un archivo CSV.

    Args:
        filas: resultados de la medición.
        ruta: archivo de destino.
    """
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


def filas_de(filas: list[dict[str, float | int | str]], nombre: str) -> tuple[list[int], list[float]]:
    """Extrae los tamaños y tiempos de una estrategia.

    Args:
        filas: resultados de la medición.
        nombre: estrategia a extraer.

    Returns:
        Tupla (tamaños, tiempos) en el orden medido.
    """
    seleccion = [f for f in filas if f["estrategia"] == nombre]
    return [int(f["n"]) for f in seleccion], [float(f["tiempo_s"]) for f in seleccion]


def pendiente_loglog(tamanos: list[int], tiempos: list[float], desde: int = 0) -> float:
    """Estima el exponente empírico k de t ≈ c · n^k.

    Ajusta una recta por mínimos cuadrados a log(t) contra log(n).

    Args:
        tamanos: tamaños de entrada.
        tiempos: tiempos medidos.
        desde: índice desde el que se ajusta (descarta tamaños muy pequeños,
            dominados por costos fijos).

    Returns:
        La pendiente de la recta, es decir, el exponente empírico.
    """
    x = np.log(np.array(tamanos[desde:], dtype=float))
    y = np.log(np.array(tiempos[desde:], dtype=float))
    return float(np.polyfit(x, y, 1)[0])


def contrastar(filas: list[dict[str, float | int | str]]) -> list[dict[str, float | int | str]]:
    """Contrasta los tiempos medidos con la complejidad teórica.

    Calcula la constante empírica c = t / f(n), donde f es la complejidad
    teórica. Si la complejidad es correcta, c se mantiene aproximadamente
    estable al crecer n.

    Args:
        filas: resultados de la medición.

    Returns:
        Una fila por medición con la complejidad, f(n) y la constante c.
    """
    contraste: list[dict[str, float | int | str]] = []
    for fila in filas:
        nombre = str(fila["estrategia"])
        etiqueta, f = COMPLEJIDAD[nombre]
        n = int(fila["n"])
        contraste.append(
            {
                "estrategia": nombre,
                "complejidad": etiqueta,
                "n": n,
                "tiempo_s": fila["tiempo_s"],
                "f_n": f(n),
                "constante_c": float(fila["tiempo_s"]) / f(n),
            }
        )
    return contraste


def graficar_comparacion(filas: list[dict[str, float | int | str]], ruta: Path) -> None:
    """Grafica tiempo contra n de voraz y regla actual en escala log-log.

    Args:
        filas: resultados de la medición.
        ruta: imagen de destino.
    """
    fig, eje = plt.subplots(figsize=(8, 5))
    for nombre, color, marca in (("voraz", "#1f77b4", "o"), ("regla_actual", "#d62728", "s")):
        tamanos, tiempos = filas_de(filas, nombre)
        etiqueta = f"{nombre.replace('_', ' ')} — teórica {COMPLEJIDAD[nombre][0]}"
        eje.plot(tamanos, tiempos, marker=marca, color=color, label=etiqueta)
    eje.axvspan(40, 120, color="#2ca02c", alpha=0.12, label="Rango real (40–120 solicitudes)")
    eje.set_xscale("log")
    eje.set_yscale("log")
    eje.set_xlabel("Número de solicitudes (n)")
    eje.set_ylabel("Tiempo (s, mediana)")
    eje.set_title("Voraz vs. regla actual (escala log-log)")
    eje.grid(True, which="both", alpha=0.3)
    eje.legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def graficar_teorica(filas: list[dict[str, float | int | str]], nombre: str, ruta: Path) -> None:
    """Superpone los tiempos medidos de una estrategia con su curva teórica.

    La curva teórica c · f(n) se escala con la constante del tamaño mayor
    medido, para comparar la forma del crecimiento.

    Args:
        filas: resultados de la medición.
        nombre: estrategia a graficar.
        ruta: imagen de destino.
    """
    tamanos, tiempos = filas_de(filas, nombre)
    etiqueta, f = COMPLEJIDAD[nombre]
    c = tiempos[-1] / f(tamanos[-1])
    fig, eje = plt.subplots(figsize=(8, 5))
    eje.plot(tamanos, tiempos, "o-", label="Medido")
    eje.plot(tamanos, [c * f(n) for n in tamanos], "--", label=f"Teórico c·{etiqueta[2:-1]}")
    if nombre != "exhaustivo":
        eje.set_xscale("log")
    eje.set_yscale("log")
    eje.set_xlabel("Número de solicitudes (n)")
    eje.set_ylabel("Tiempo (s, mediana)")
    eje.set_title(f"{nombre.replace('_', ' ').capitalize()}: medido vs. {etiqueta}")
    eje.grid(True, which="both", alpha=0.3)
    eje.legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def main() -> None:
    """Ejecuta el experimento completo y guarda tablas y gráficas."""
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)
    filas: list[dict[str, float | int | str]] = []
    print("Midiendo...")
    for nombre, tamanos in TAMANOS.items():
        filas.extend(medir_estrategia(nombre, tamanos))

    guardar_csv(filas, CARPETA_RESULTADOS / "tiempos.csv")
    guardar_csv(contrastar(filas), CARPETA_RESULTADOS / "contraste_complejidad.csv")

    graficar_comparacion(filas, CARPETA_GRAFICAS / "voraz_vs_regla_actual.png")
    for nombre in ESTRATEGIAS:
        graficar_teorica(filas, nombre, CARPETA_GRAFICAS / f"{nombre}_teorica.png")

    print("\nExponente empirico (t = c * n^k), ajustado desde n >= 250:")
    for nombre in ("voraz", "regla_actual"):
        tamanos, tiempos = filas_de(filas, nombre)
        print(f"  {nombre:<13} k = {pendiente_loglog(tamanos, tiempos, desde=3):.2f}")
    tamanos, tiempos = filas_de(filas, "exhaustivo")
    razones = [tiempos[i + 1] / tiempos[i] for i in range(len(tiempos) - 1)]
    print(f"  exhaustivo    razon t(n+2)/t(n) promedio = {statistics.mean(razones[2:]):.2f} (teorica 4*(n+2)/n = 4.4-5.0)")
    print(f"\nResultados en {CARPETA_RESULTADOS} y gráficas en {CARPETA_GRAFICAS}")


if __name__ == "__main__":
    main()
