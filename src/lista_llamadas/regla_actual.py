"""Proceso actual: ordenamiento por inserción de todos los pendientes."""

from modelo import Resultado, clave_prioridad


def lista_por_insercion(pendientes: list[Resultado], k: int) -> list[Resultado]:
    """Reproduce el proceso actual de la lista de llamadas.

    Ordena una copia de TODOS los pendientes con ordenamiento por inserción,
    O(n²) en el peor caso y en el caso promedio, y se queda con los primeros
    k aunque solo esos se usen.

    Args:
        pendientes: resultados pendientes (no se modifican).
        k: capacidad de llamadas del día.

    Returns:
        Los k resultados de mayor prioridad, en orden de llamada.
    """
    ordenados = list(pendientes)
    for i in range(1, len(ordenados)):
        actual = ordenados[i]
        clave_actual = clave_prioridad(actual)
        j = i - 1
        while j >= 0 and clave_prioridad(ordenados[j]) > clave_actual:
            ordenados[j + 1] = ordenados[j]
            j -= 1
        ordenados[j + 1] = actual
    return ordenados[:k]
