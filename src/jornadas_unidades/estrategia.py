"""Programación de las jornadas de una unidad móvil (estrategia voraz).

Criterio del equipo: maximizar el NÚMERO de jornadas atendidas. Los pacientes
de alto riesgo se conservan en cada solicitud pero no intervienen en la
decisión. Convención de borde: el intervalo es [inicio, fin), de modo que una
jornada que empieza justo cuando otra termina NO se cruza.
"""

# (inicio, fin, pacientes_alto_riesgo); inicio y fin en minutos.
Jornada = tuple[int, int, int]


def seleccionar_jornadas(solicitudes: list[Jornada]) -> list[Jornada]:
    """Elige las jornadas que atiende la unidad, sin cruces.

    Estrategia voraz: ordena por hora de fin (ordenamiento estable, así que en
    un empate gana la que llegó primero) y acepta cada solicitud cuyo inicio
    sea mayor o igual al fin de la última jornada aceptada.

    Args:
        solicitudes: solicitudes del mes de una subregión.

    Returns:
        Las jornadas elegidas, ordenadas por hora de inicio. Maximiza el
        número de jornadas.
    """
    elegidas: list[Jornada] = []
    for jornada in sorted(solicitudes, key=lambda j: j[1]):
        if not elegidas or jornada[0] >= elegidas[-1][1]:
            elegidas.append(jornada)
    return elegidas


def hay_cruce(jornadas: list[Jornada]) -> bool:
    """Indica si alguna pareja de jornadas se cruza.

    Una jornada que empieza justo cuando otra termina no se considera cruce.
    Supone que cada jornada tiene inicio < fin. Ordenadas por inicio, basta
    revisar las parejas consecutivas.

    Args:
        jornadas: jornadas a revisar.

    Returns:
        True si dos jornadas se cruzan; False en caso contrario.
    """
    ordenadas = sorted(jornadas, key=lambda j: (j[0], j[1]))
    return any(
        ordenadas[i][1] > ordenadas[i + 1][0] for i in range(len(ordenadas) - 1)
    )


def valor(jornadas: list[Jornada]) -> int:
    """Calcula el valor de una programación según el criterio del equipo.

    Args:
        jornadas: jornadas programadas.

    Returns:
        El número de jornadas (el criterio es maximizar esa cantidad).
    """
    return len(jornadas)