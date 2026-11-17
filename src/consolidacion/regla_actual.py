"""Proceso actual: busca a cada paciente recorriendo la lista consolidada."""

from modelo import Resultado, es_mas_reciente, paciente


def consolidar_busqueda_lineal(resultados: list[Resultado]) -> list[Resultado]:
    """Reproduce el proceso actual de consolidación.

    Toma cada resultado nuevo y busca al paciente recorriendo la lista ya
    consolidada. Si lo encuentra, conserva el más reciente; si no, lo agrega.
    Cada búsqueda cuesta O(m), con m el tamaño de la lista consolidada, así
    que el total es O(n · m) ≈ O(n²).

    Args:
        resultados: resultados en el orden en que llegaron (no se modifican).

    Returns:
        Un resultado por paciente, el más reciente, en orden de primera
        aparición del paciente.
    """
    consolidados: list[Resultado] = []
    for resultado in resultados:
        llave = paciente(resultado)
        for i, existente in enumerate(consolidados):
            if paciente(existente) == llave:
                if es_mas_reciente(resultado, existente):
                    consolidados[i] = resultado
                break
        else:
            consolidados.append(resultado)
    return consolidados
