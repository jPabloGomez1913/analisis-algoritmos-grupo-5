"""Estructura de un resultado pendiente y el orden de prioridad de llamada.

Un resultado es una tupla inmutable (NamedTuple): ninguna estrategia modifica
los registros originales, solo elige cuáles van en la lista y en qué orden.
"""

from typing import NamedTuple

CAPACIDAD_DIARIA = 9_000


class Resultado(NamedTuple):
    """Resultado pendiente de gestión (ya consolidado: uno por paciente)."""

    tipo_documento: str
    numero_documento: str
    id_laboratorio: int
    id_lote: int
    fecha_resultado: int  # minutos desde una fecha base (menor = más antiguo)
    indice_riesgo: int  # entero entre 0 y 100
    municipio: str


Clave = tuple[int, int, str, str]


def clave_prioridad(resultado: Resultado) -> Clave:
    """Clave de orden de la lista de llamadas (menor clave = se llama antes).

    Primero el mayor índice de riesgo; a igual riesgo, el resultado más
    antiguo (restricción del negocio). Si también coincide la fecha, se
    desempata por documento para que el orden sea total y reproducible.

    Args:
        resultado: resultado pendiente.

    Returns:
        La tupla (-riesgo, fecha, tipo_documento, numero_documento).
    """
    return (
        -resultado.indice_riesgo,
        resultado.fecha_resultado,
        resultado.tipo_documento,
        resultado.numero_documento,
    )
