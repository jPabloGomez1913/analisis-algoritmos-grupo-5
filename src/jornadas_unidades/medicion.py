"""Medición experimental del desempeño de las estrategias de jornadas.

Mide el tiempo y cuenta las operaciones elementales de las tres soluciones
(voraz, regla actual por orden de llegada y exhaustiva) sobre instancias
sintéticas de tamaño creciente. En cada tamaño, las tres soluciones reciben
las mismas instancias. El propio experimento verifica que la estrategia voraz
obtiene el mismo valor que la exhaustiva. Los resultados se guardan en CSV, se
generan las gráficas y se contrasta lo medido con la complejidad teórica.

Uso (desde src/jornadas_unidades):
    python medicion.py
"""

import csv
import gc
import math
import statistics
import time
from functools import cmp_to_key
from pathlib import Path
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")  # genera las imágenes sin abrir ventanas
import matplotlib.pyplot as plt
import numpy as np

from datos import generar_instancia
from estrategia import Jornada, hay_cruce, seleccionar_jornadas, valor
from exhaustivo import seleccionar_exhaustivo
from regla_actual import asignar_por_llegada

Estrategia = Callable[[list[Jornada]], list[Jornada]]
Contadora = Callable[[list[Jornada]], tuple[list[Jornada], int]]
Fila = dict[str, Any]

OPERACION = "jornadas_unidades"
RAIZ = Path(__file__).resolve().parents[2]
CARPETA_RESULTADOS = RAIZ / "resultados" / OPERACION
CARPETA_GRAFICAS = RAIZ / "graficas" / OPERACION

# Tamaños comunes: las tres soluciones corren sobre ellos, así que sirven para
# verificar que voraz y exhaustiva coinciden. Incluyen parejas donde el
# segundo es el doble del primero (4-8, 6-12, 8-16, 10-20). Los tamaños grandes solo
# los corren la voraz y la regla actual (la exhaustiva ya no termina); el
# rango real del caso (40 a 120 solicitudes por subregión) está incluido.
TAMANOS_COMUNES = [4, 6, 8, 10, 12, 14, 16, 18, 20]
TAMANOS_GRANDES = [40, 80, 120, 250, 500, 1_000, 2_000, 4_000, 8_000, 16_000]
TAMANOS_SOLO_VORAZ = [32_000, 64_000]

TAMANOS: dict[str, list[int]] = {
    "voraz": TAMANOS_COMUNES + TAMANOS_GRANDES + TAMANOS_SOLO_VORAZ,
    "regla_actual": TAMANOS_COMUNES + TAMANOS_GRANDES,
    "exhaustivo": TAMANOS_COMUNES,
}

ESTRATEGIAS: dict[str, Estrategia] = {
    "voraz": seleccionar_jornadas,
    "regla_actual": asignar_por_llegada,
    "exhaustivo": seleccionar_exhaustivo,
}

# Complejidad teórica del tiempo, como función de n.
COMPLEJIDAD: dict[str, tuple[str, Callable[[int], float]]] = {
    "voraz": ("O(n log n)", lambda n: n * math.log2(n)),
    "regla_actual": ("O(n²)", lambda n: float(n * n)),
    "exhaustivo": ("O(2ⁿ · n)", lambda n: (2.0**n) * n),
}

# Complejidad teórica del número de operaciones elementales contadas.
COMPLEJIDAD_OPERACIONES: dict[str, tuple[str, Callable[[int], float]]] = {
    "voraz": ("O(n log n)", lambda n: n * math.log2(n)),
    "regla_actual": ("O(n²)", lambda n: float(n * n)),
    "exhaustivo": ("O(2ⁿ)", lambda n: 2.0**n),
}

ESTILOS: dict[str, tuple[str, str]] = {
    "voraz": ("#1f77b4", "o"),
    "regla_actual": ("#d62728", "s"),
    "exhaustivo": ("#ff7f0e", "^"),
}

REPETICIONES = 5
SEMILLAS = (11, 23, 37)


# ---------------------------------------------------------------------------
# Contadores de operaciones elementales
#
# Cada función repite la lógica de su estrategia y agrega un contador propio.
# No se cronometran: el tiempo se mide solo sobre las funciones originales.
# main() verifica que cada una devuelve el mismo valor que la original.
# ---------------------------------------------------------------------------


def ordenar_contando(
    elementos: list[Jornada], clave: Callable[[Jornada], Any]
) -> tuple[list[Jornada], int]:
    """Ordena una lista contando las comparaciones que hace el ordenamiento.

    Args:
        elementos: elementos a ordenar.
        clave: función que devuelve la clave de ordenamiento de un elemento.

    Returns:
        Tupla (lista ordenada, número de comparaciones realizadas).
    """
    comparaciones = 0

    def comparar(a: Jornada, b: Jornada) -> int:
        nonlocal comparaciones
        comparaciones += 1
        clave_a, clave_b = clave(a), clave(b)
        return (clave_a > clave_b) - (clave_a < clave_b)

    return sorted(elementos, key=cmp_to_key(comparar)), comparaciones


def contar_voraz(solicitudes: list[Jornada]) -> tuple[list[Jornada], int]:
    """Estrategia voraz contando comparaciones.

    Cuenta las comparaciones del ordenamiento por hora de fin y una
    comparación por solicitud en el recorrido de selección.

    Args:
        solicitudes: solicitudes del mes de una subregión.

    Returns:
        Tupla (jornadas elegidas, operaciones contadas).
    """
    ordenadas, operaciones = ordenar_contando(solicitudes, lambda j: j[1])
    elegidas: list[Jornada] = []
    for jornada in ordenadas:
        operaciones += 1
        if not elegidas or jornada[0] >= elegidas[-1][1]:
            elegidas.append(jornada)
    return elegidas, operaciones


def contar_regla_actual(solicitudes: list[Jornada]) -> tuple[list[Jornada], int]:
    """Regla actual (orden de llegada) contando comparaciones de cruce.

    Cuenta cada comparación contra una jornada ya aceptada (con el mismo
    corte anticipado que la regla original) y las comparaciones del
    ordenamiento final.

    Args:
        solicitudes: solicitudes en el orden en que llegaron.

    Returns:
        Tupla (jornadas aceptadas, operaciones contadas).
    """
    aceptadas: list[Jornada] = []
    operaciones = 0
    for inicio, fin, pacientes in solicitudes:
        libre = True
        for aceptada in aceptadas:
            operaciones += 1
            if not (fin <= aceptada[0] or inicio >= aceptada[1]):
                libre = False
                break
        if libre:
            aceptadas.append((inicio, fin, pacientes))
    ordenadas, comparaciones = ordenar_contando(aceptadas, lambda j: (j[0], j[1]))
    return ordenadas, operaciones + comparaciones


def contar_exhaustivo(solicitudes: list[Jornada]) -> tuple[list[Jornada], int]:
    """Solución exhaustiva contando los subconjuntos explorados.

    Args:
        solicitudes: solicitudes del mes de una subregión.

    Returns:
        Tupla (mejor subconjunto, subconjuntos explorados).
    """
    ordenadas = sorted(solicitudes, key=lambda j: (j[0], j[1]))
    n = len(ordenadas)
    mejor: list[Jornada] = []
    operaciones = 0
    for mascara in range(1, 1 << n):
        operaciones += 1
        subconjunto = [ordenadas[i] for i in range(n) if (mascara >> i) & 1]
        if len(subconjunto) > len(mejor) and not hay_cruce(subconjunto):
            mejor = subconjunto
    return mejor, operaciones


CONTADORAS: dict[str, Contadora] = {
    "voraz": contar_voraz,
    "regla_actual": contar_regla_actual,
    "exhaustivo": contar_exhaustivo,
}


# ---------------------------------------------------------------------------
# Medición
# ---------------------------------------------------------------------------


def medir_tiempo(
    estrategia: Estrategia, instancia: list[Jornada], repeticiones: int
) -> tuple[float, list[Jornada]]:
    """Mide el tiempo de una estrategia sobre una instancia.

    Ejecuta la estrategia varias veces con time.perf_counter y devuelve la
    mediana, que es menos sensible que el promedio a interrupciones del
    sistema operativo. Solo se cronometra la ejecución, nunca la generación
    de los datos. Se desactiva el recolector de basura durante la medición
    (igual que hace timeit) para que sus pausas no metan ruido en el tiempo.

    Args:
        estrategia: función que recibe las solicitudes y devuelve las jornadas.
        instancia: solicitudes de entrada (no se modifican).
        repeticiones: número de ejecuciones a medir.

    Returns:
        Tupla (mediana del tiempo en segundos, resultado de la última corrida).
    """
    tiempos: list[float] = []
    resultado: list[Jornada] = []
    gc.disable()
    try:
        for _ in range(repeticiones):
            inicio = time.perf_counter()
            resultado = estrategia(instancia)
            tiempos.append(time.perf_counter() - inicio)
    finally:
        gc.enable()
    return statistics.median(tiempos), resultado


def repeticiones_para(nombre: str, n: int) -> int:
    """Define cuántas repeticiones se miden según la estrategia y el tamaño.

    Args:
        nombre: clave de la estrategia en ESTRATEGIAS.
        n: tamaño de la instancia.

    Returns:
        Número de repeticiones de la medición.
    """
    if nombre == "exhaustivo" and n >= 16:
        return 1
    if n >= 8_000:
        return 3
    return REPETICIONES


def verificar(resultados: dict[str, list[Jornada]], n: int, semilla: int) -> None:
    """Verifica dentro del experimento que las soluciones son correctas.

    Comprueba que ninguna solución tenga jornadas cruzadas, que la regla
    actual nunca supere a la voraz y que la voraz obtenga el mismo valor que
    la exhaustiva en los tamaños donde ambas corren.

    Args:
        resultados: jornadas elegidas por cada estrategia en la instancia.
        n: tamaño de la instancia (para el mensaje de error).
        semilla: semilla de la instancia (para el mensaje de error).
    """
    for nombre, elegidas in resultados.items():
        assert not hay_cruce(elegidas), (nombre, n, semilla)
    if "regla_actual" in resultados:
        assert valor(resultados["regla_actual"]) <= valor(resultados["voraz"]), (
            n,
            semilla,
        )
    if "exhaustivo" in resultados:
        assert valor(resultados["voraz"]) == valor(resultados["exhaustivo"]), (
            n,
            semilla,
        )


def medir_experimento() -> list[Fila]:
    """Ejecuta el experimento completo sobre todos los tamaños.

    Para cada tamaño se generan instancias con semilla fija (una por semilla)
    y todas las estrategias que corren en ese tamaño reciben las mismas.

    Returns:
        Una fila por estrategia y tamaño con tiempo (mediana entre semillas),
        operaciones y jornadas elegidas (promedios entre semillas).
    """
    filas: list[Fila] = []
    todos = sorted({n for tamanos in TAMANOS.values() for n in tamanos})
    print("Midiendo...")
    for n in todos:
        nombres = [nombre for nombre in ESTRATEGIAS if n in TAMANOS[nombre]]
        datos: dict[str, dict[str, list[float]]] = {
            nombre: {"tiempos": [], "operaciones": [], "jornadas": []}
            for nombre in nombres
        }
        for semilla in SEMILLAS:
            instancia = generar_instancia(n, semilla)  # misma para todas
            resultados: dict[str, list[Jornada]] = {}
            for nombre in nombres:
                tiempo, real = medir_tiempo(
                    ESTRATEGIAS[nombre], instancia, repeticiones_para(nombre, n)
                )
                contada, operaciones = CONTADORAS[nombre](instancia)
                # El contador debe reproducir exactamente la estrategia real.
                assert valor(contada) == valor(real), (nombre, n, semilla)
                resultados[nombre] = real
                datos[nombre]["tiempos"].append(tiempo)
                datos[nombre]["operaciones"].append(operaciones)
                datos[nombre]["jornadas"].append(valor(real))
            verificar(resultados, n, semilla)
        for nombre in nombres:
            fila: Fila = {
                "estrategia": nombre,
                "n": n,
                "tiempo_s": statistics.median(datos[nombre]["tiempos"]),
                "operaciones": round(statistics.mean(datos[nombre]["operaciones"])),
                "jornadas_elegidas": round(
                    statistics.mean(datos[nombre]["jornadas"]), 1
                ),
            }
            filas.append(fila)
            print(
                f"  {nombre:<13} n={n:>6}  {fila['tiempo_s']:.6f} s"
                f"  {fila['operaciones']:>14,} ops"
            )
    return filas


# ---------------------------------------------------------------------------
# Análisis: contraste con la teoría
# ---------------------------------------------------------------------------


def extraer(filas: list[Fila], nombre: str, columna: str) -> tuple[list[int], list[float]]:
    """Extrae los tamaños y una columna de resultados de una estrategia.

    Args:
        filas: resultados de la medición.
        nombre: estrategia a extraer.
        columna: columna a extraer ("tiempo_s" u "operaciones").

    Returns:
        Tupla (tamaños, valores) en el orden medido.
    """
    seleccion = [f for f in filas if f["estrategia"] == nombre]
    return [int(f["n"]) for f in seleccion], [float(f[columna]) for f in seleccion]


def pendiente_loglog(
    filas: list[Fila], nombre: str, columna: str, desde_n: int = 250
) -> float:
    """Estima el exponente empírico k de valor ≈ c · n^k.

    Ajusta una recta por mínimos cuadrados a log(valor) contra log(n),
    usando solo los tamaños n >= desde_n (los muy pequeños están dominados
    por costos fijos).

    Args:
        filas: resultados de la medición.
        nombre: estrategia a analizar.
        columna: "tiempo_s" u "operaciones".
        desde_n: tamaño mínimo que entra en el ajuste.

    Returns:
        La pendiente de la recta, es decir, el exponente empírico.
    """
    tamanos, valores = extraer(filas, nombre, columna)
    pares = [(n, v) for n, v in zip(tamanos, valores) if n >= desde_n]
    x = np.log(np.array([n for n, _ in pares], dtype=float))
    y = np.log(np.array([v for _, v in pares], dtype=float))
    return float(np.polyfit(x, y, 1)[0])


def contrastar(filas: list[Fila]) -> list[Fila]:
    """Contrasta lo medido con la complejidad teórica.

    Calcula las constantes empíricas c = t / f(n) y c = operaciones / g(n),
    donde f y g son las complejidades teóricas. Si la complejidad es correcta,
    la constante se mantiene aproximadamente estable al crecer n.

    Args:
        filas: resultados de la medición.

    Returns:
        Una fila por medición con las funciones teóricas y las constantes.
    """
    contraste: list[Fila] = []
    for fila in filas:
        nombre = str(fila["estrategia"])
        n = int(fila["n"])
        etiqueta_t, f = COMPLEJIDAD[nombre]
        etiqueta_o, g = COMPLEJIDAD_OPERACIONES[nombre]
        contraste.append(
            {
                "estrategia": nombre,
                "n": n,
                "complejidad_tiempo": etiqueta_t,
                "constante_c_tiempo": float(fila["tiempo_s"]) / f(n),
                "complejidad_operaciones": etiqueta_o,
                "constante_c_operaciones": float(fila["operaciones"]) / g(n),
            }
        )
    return contraste


def factores_duplicacion(filas: list[Fila]) -> list[Fila]:
    """Calcula cuánto crece el tiempo y las operaciones al duplicar n.

    Para cada pareja de tamaños (n, 2n) medida, compara el factor observado
    con el que predice la complejidad teórica.

    Args:
        filas: resultados de la medición.

    Returns:
        Una fila por pareja (n, 2n) y estrategia.
    """
    resultado: list[Fila] = []
    for nombre in ESTRATEGIAS:
        tamanos, tiempos = extraer(filas, nombre, "tiempo_s")
        _, operaciones = extraer(filas, nombre, "operaciones")
        posicion = {n: i for i, n in enumerate(tamanos)}
        f = COMPLEJIDAD[nombre][1]
        g = COMPLEJIDAD_OPERACIONES[nombre][1]
        for n in tamanos:
            if 2 * n in posicion:
                i, j = posicion[n], posicion[2 * n]
                resultado.append(
                    {
                        "estrategia": nombre,
                        "n": n,
                        "2n": 2 * n,
                        "factor_tiempo": tiempos[j] / tiempos[i],
                        "esperado_tiempo": f(2 * n) / f(n),
                        "factor_operaciones": operaciones[j] / operaciones[i],
                        "esperado_operaciones": g(2 * n) / g(n),
                    }
                )
    return resultado


# ---------------------------------------------------------------------------
# Salidas: CSV y gráficas
# ---------------------------------------------------------------------------


def guardar_csv(filas: list[Fila], ruta: Path) -> None:
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


def graficar_metrica(
    filas: list[Fila],
    columna: str,
    unidad_y: str,
    titulo: str,
    teorica: dict[str, tuple[str, Callable[[int], float]]],
    ruta: Path,
) -> None:
    """Grafica una métrica contra n, con las tres soluciones en los mismos ejes.

    Args:
        filas: resultados de la medición.
        columna: "tiempo_s" u "operaciones".
        unidad_y: texto del eje y, con unidades.
        titulo: título de la gráfica.
        teorica: complejidad teórica de cada estrategia (para la leyenda).
        ruta: imagen de destino.
    """
    fig, eje = plt.subplots(figsize=(9, 5.5))
    for nombre, (color, marca) in ESTILOS.items():
        tamanos, valores = extraer(filas, nombre, columna)
        etiqueta = f"{nombre.replace('_', ' ')} (teórica {teorica[nombre][0]})"
        eje.plot(tamanos, valores, marker=marca, color=color, label=etiqueta)
    eje.axvspan(40, 120, color="#2ca02c", alpha=0.12, label="Rango real (40–120 solicitudes)")
    eje.set_xscale("log")
    eje.set_yscale("log")
    eje.set_xlabel("Número de solicitudes (n)")
    eje.set_ylabel(unidad_y)
    eje.set_title(titulo)
    eje.grid(True, which="both", alpha=0.3)
    eje.legend()
    fig.tight_layout()
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
    tamanos, tiempos = extraer(filas, nombre, "tiempo_s")
    etiqueta, f = COMPLEJIDAD[nombre]
    c = tiempos[-1] / f(tamanos[-1])
    fig, eje = plt.subplots(figsize=(8, 5))
    eje.plot(tamanos, tiempos, "o-", label="Medido")
    eje.plot(tamanos, [c * f(n) for n in tamanos], "--", label=f"Teórico c · {etiqueta}")
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
    filas = medir_experimento()
    factores = factores_duplicacion(filas)

    guardar_csv(filas, CARPETA_RESULTADOS / "tiempos.csv")
    guardar_csv(contrastar(filas), CARPETA_RESULTADOS / "contraste_complejidad.csv")
    guardar_csv(factores, CARPETA_RESULTADOS / "factores_duplicacion.csv")

    graficar_metrica(
        filas,
        "tiempo_s",
        "Tiempo de ejecución (s, mediana)",
        "Tiempo vs. tamaño de entrada (escala log-log)",
        COMPLEJIDAD,
        CARPETA_GRAFICAS / "tiempo_vs_n.png",
    )
    graficar_metrica(
        filas,
        "operaciones",
        "Operaciones elementales (número)",
        "Operaciones vs. tamaño de entrada (escala log-log)",
        COMPLEJIDAD_OPERACIONES,
        CARPETA_GRAFICAS / "operaciones_vs_n.png",
    )
    for nombre in ESTRATEGIAS:
        graficar_teorica(filas, nombre, CARPETA_GRAFICAS / f"{nombre}_teorica.png")

    print("\nFactor de crecimiento al duplicar n (observado vs. esperado):")
    for f in factores:
        print(
            f"  {f['estrategia']:<13} {f['n']:>6} -> {f['2n']:>6}"
            f"  tiempo x{f['factor_tiempo']:.2f} (esp. {f['esperado_tiempo']:.2f})"
            f"  ops x{f['factor_operaciones']:.2f} (esp. {f['esperado_operaciones']:.2f})"
        )

    print("\nExponente empirico (valor = c * n^k), ajustado desde n >= 250:")
    for nombre in ("voraz", "regla_actual"):
        k_tiempo = pendiente_loglog(filas, nombre, "tiempo_s")
        k_ops = pendiente_loglog(filas, nombre, "operaciones")
        print(f"  {nombre:<13} k_tiempo = {k_tiempo:.2f}   k_operaciones = {k_ops:.2f}")

    print(f"\nResultados en {CARPETA_RESULTADOS}")
    print(f"Graficas en {CARPETA_GRAFICAS}")


if __name__ == "__main__":
    main()