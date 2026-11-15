"""Solución exhaustiva: prueba todos los subconjuntos de solicitudes."""

from estrategia import Jornada, hay_cruce


def seleccionar_exhaustivo(solicitudes: list[Jornada]) -> list[Jornada]:
    """Elige el mejor subconjunto sin cruces probando todos los subconjuntos.

    Recorre las 2^n máscaras de bits, descarta los subconjuntos con cruces y
    se queda con el de mayor número de jornadas. Solo para instancias
    pequeñas (hasta unas dos decenas de solicitudes).

    Args:
        solicitudes: solicitudes del mes de una subregión.

    Returns:
        Un subconjunto óptimo para el mismo criterio, ordenado por inicio.
    """
    ordenadas = sorted(solicitudes, key=lambda j: (j[0], j[1]))
    n = len(ordenadas)
    mejor: list[Jornada] = []
    for mascara in range(1 << n):
        subconjunto = [ordenadas[i] for i in range(n) if (mascara >> i) & 1]
        if len(subconjunto) > len(mejor) and not hay_cruce(subconjunto):
            mejor = subconjunto
    return mejor
