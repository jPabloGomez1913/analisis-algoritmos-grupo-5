"""Generador de instancias sintéticas con semilla fija."""

import random

from estrategia import Jornada


def generar_instancia(
    n: int,
    semilla: int,
    duracion_min: int = 60,
    duracion_max: int = 480,
    minutos_por_solicitud: int = 180,
) -> list[Jornada]:
    """Genera n solicitudes en orden de llegada, con cruces reales.

    El horizonte crece con n (n * minutos_por_solicitud) para que la densidad
    de cruces se mantenga al variar el tamaño.

    Args:
        n: número de solicitudes.
        semilla: semilla del generador, para reproducir la instancia.
        duracion_min: duración mínima de una jornada, en minutos.
        duracion_max: duración máxima de una jornada, en minutos.
        minutos_por_solicitud: minutos de horizonte por cada solicitud.

    Returns:
        Lista de (inicio, fin, pacientes_alto_riesgo) con inicio < fin.
    """
    azar = random.Random(semilla)
    horizonte = max(n * minutos_por_solicitud, duracion_max + 1)
    solicitudes: list[Jornada] = []
    for _ in range(n):
        duracion = azar.randint(duracion_min, duracion_max)
        inicio = azar.randint(0, horizonte - duracion)
        solicitudes.append((inicio, inicio + duracion, azar.randint(1, 40)))
    return solicitudes
