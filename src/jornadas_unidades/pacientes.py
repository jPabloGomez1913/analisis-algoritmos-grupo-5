"""Pacientes de alto riesgo atendidos por cada estrategia (apoyo a la sección 6).

El criterio del equipo es maximizar el número de jornadas; los pacientes no
intervienen en la decisión. Este script mide, sobre las mismas instancias
sintéticas de medicion.py, cuántos pacientes de alto riesgo quedan en las
jornadas que elige la voraz y la regla actual, y los compara con el máximo
posible si el criterio fuera maximizar pacientes (selección ponderada de
intervalos, resuelta por programación dinámica). Escribe
resultados/jornadas_unidades/pacientes.csv.

Uso (desde src/jornadas_unidades):
    python pacientes.py
"""

import csv
import statistics
from bisect import bisect_right
from pathlib import Path

from datos import generar_instancia
from estrategia import Jornada, hay_cruce, seleccionar_jornadas
from regla_actual import asignar_por_llegada

RAIZ = Path(__file__).resolve().parents[2]
RUTA_CSV = RAIZ / "resultados" / "jornadas_unidades" / "pacientes.csv"

TAMANOS = [40, 80, 120]  # rango real del caso
SEMILLAS = (11, 23, 37)  # las mismas de medicion.py


def pacientes(jornadas: list[Jornada]) -> int:
    """Suma los pacientes de alto riesgo de las jornadas dadas.

    Args:
        jornadas: jornadas elegidas por una estrategia.

    Returns:
        Total de pacientes de alto riesgo en esas jornadas.
    """
    return sum(j[2] for j in jornadas)


def optimo_ponderado(solicitudes: list[Jornada]) -> int:
    """Máximo de pacientes atendibles sin cruces (programación dinámica).

    Ordena por hora de fin. mejor[i] es el máximo usando las primeras i
    solicitudes: o se descarta la i-ésima, o se toma y se suma lo mejor
    posible entre las que terminan a más tardar cuando ella empieza
    (intervalos [inicio, fin), así que terminar justo al inicio es compatible).

    Args:
        solicitudes: solicitudes del mes de una subregión.

    Returns:
        La mayor suma de pacientes de un subconjunto sin cruces.
    """
    ordenadas = sorted(solicitudes, key=lambda j: j[1])
    fines = [j[1] for j in ordenadas]
    mejor = [0] * (len(ordenadas) + 1)
    for i, (inicio, _fin, personas) in enumerate(ordenadas, start=1):
        previas = bisect_right(fines, inicio, 0, i - 1)
        mejor[i] = max(mejor[i - 1], mejor[previas] + personas)
    return mejor[-1]


def optimo_fuerza_bruta(solicitudes: list[Jornada]) -> int:
    """Calcula lo mismo que optimo_ponderado, probando todos los subconjuntos.

    Solo sirve para verificar la programación dinámica en instancias
    pequeñas: su costo es exponencial.

    Args:
        solicitudes: solicitudes del mes de una subregión (pocas).

    Returns:
        La mayor suma de pacientes de un subconjunto sin cruces.
    """
    n = len(solicitudes)
    mejor = 0
    for mascara in range(1 << n):
        elegidas = [solicitudes[i] for i in range(n) if (mascara >> i) & 1]
        if not hay_cruce(elegidas):
            mejor = max(mejor, pacientes(elegidas))
    return mejor


def verificar_dinamica() -> None:
    """Comprueba la programación dinámica contra fuerza bruta (n <= 12).

    Usa 30 instancias aleatorias de 6 a 12 solicitudes con semilla fija.
    Si alguna no coincide, el assert muestra la semilla y la instancia.
    """
    for semilla in range(30):
        instancia = generar_instancia(6 + semilla % 7, semilla)
        assert optimo_ponderado(instancia) == optimo_fuerza_bruta(instancia), (
            semilla,
            instancia,
        )


def main() -> None:
    """Calcula las cifras de pacientes y guarda el CSV."""
    verificar_dinamica()
    filas: list[dict[str, float | int]] = []
    for n in TAMANOS:
        voraz: list[int] = []
        regla: list[int] = []
        optimo: list[int] = []
        for semilla in SEMILLAS:
            instancia = generar_instancia(n, semilla)
            voraz.append(pacientes(seleccionar_jornadas(instancia)))
            regla.append(pacientes(asignar_por_llegada(instancia)))
            optimo.append(optimo_ponderado(instancia))
        fila: dict[str, float | int] = {
            "n": n,
            "pacientes_voraz": round(statistics.mean(voraz)),
            "pacientes_regla_actual": round(statistics.mean(regla)),
            "pacientes_optimo_ponderado": round(statistics.mean(optimo)),
        }
        fila["voraz_sobre_optimo"] = round(
            statistics.mean(voraz) / statistics.mean(optimo), 3
        )
        fila["regla_sobre_optimo"] = round(
            statistics.mean(regla) / statistics.mean(optimo), 3
        )
        filas.append(fila)
        print(fila)
    RUTA_CSV.parent.mkdir(parents=True, exist_ok=True)
    with RUTA_CSV.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


if __name__ == "__main__":
    main()