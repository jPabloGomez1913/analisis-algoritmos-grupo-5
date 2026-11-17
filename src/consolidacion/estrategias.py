"""Estrategias propuestas para consolidar los pacientes repetidos.

Restricción del negocio: de cada paciente queda exactamente un resultado, el
más reciente, y ningún paciente desaparece. Las dos estrategias devuelven el
mismo conjunto de resultados que la regla actual.
"""

from modelo import Resultado, es_mas_reciente, paciente


def consolidar_con_diccionario(resultados: list[Resultado]) -> list[Resultado]:
    """Estrategia A: tabla hash indexada por paciente.

    Recorre los resultados una sola vez. El diccionario responde en O(1)
    promedio si el paciente ya existe, así que el costo total es O(n) en
    tiempo y O(p) en espacio, con p el número de pacientes distintos.

    Args:
        resultados: resultados en el orden en que llegaron (no se modifican).

    Returns:
        Un resultado por paciente, el más reciente, en orden de primera
        aparición del paciente (los diccionarios conservan ese orden).
    """
    por_paciente: dict[tuple[str, str], Resultado] = {}
    for resultado in resultados:
        llave = paciente(resultado)
        actual = por_paciente.get(llave)
        if actual is None or es_mas_reciente(resultado, actual):
            por_paciente[llave] = resultado
    return list(por_paciente.values())


def consolidar_ordenando(resultados: list[Resultado]) -> list[Resultado]:
    """Estrategia B: ordenar por paciente y fecha, y quedarse con el último.

    Ordena una copia por (paciente, fecha) con el ordenamiento de Python
    (Timsort, un mergesort adaptativo: dividir y vencer, O(n log n)). Como el
    ordenamiento es estable, a igual fecha queda al final el que llegó
    después. Luego un recorrido lineal conserva el último resultado de cada
    grupo de paciente. Tiempo O(n log n), espacio O(n).

    Args:
        resultados: resultados en el orden en que llegaron (no se modifican).

    Returns:
        Un resultado por paciente, el más reciente, ordenados por documento.
    """
    ordenados = sorted(resultados, key=lambda r: (paciente(r), r.fecha_resultado))
    consolidados: list[Resultado] = []
    for i, resultado in enumerate(ordenados):
        es_ultimo_del_paciente = (
            i == len(ordenados) - 1 or paciente(ordenados[i + 1]) != paciente(resultado)
        )
        if es_ultimo_del_paciente:
            consolidados.append(resultado)
    return consolidados
