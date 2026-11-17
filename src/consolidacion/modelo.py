"""Estructura de un resultado de laboratorio y criterio de "más reciente".

Un resultado es una tupla inmutable (NamedTuple), de modo que ninguna
estrategia puede modificar los registros originales enviados por los
laboratorios: solo se eligen cuáles se conservan.
"""

from typing import NamedTuple


class Resultado(NamedTuple):
    """Resultado de una prueba de tamizaje reportado por un laboratorio."""

    tipo_documento: str
    numero_documento: str
    id_laboratorio: int
    id_lote: int
    fecha_resultado: int  # minutos desde una fecha base (mayor = más reciente)
    indice_riesgo: int  # entero entre 0 y 100
    municipio: str


Paciente = tuple[str, str]  # (tipo_documento, numero_documento)


def paciente(resultado: Resultado) -> Paciente:
    """Devuelve la llave que identifica al paciente de un resultado.

    Args:
        resultado: resultado de laboratorio.

    Returns:
        La tupla (tipo_documento, numero_documento).
    """
    return (resultado.tipo_documento, resultado.numero_documento)


def es_mas_reciente(nuevo: Resultado, actual: Resultado) -> bool:
    """Indica si un resultado debe reemplazar al que se tiene del paciente.

    Gana la fecha mayor. Si las fechas son iguales gana el que llegó después
    (el último reportado), para que todas las estrategias den el mismo
    resultado aun en ese empate.

    Args:
        nuevo: resultado que llega después en el orden de entrada.
        actual: resultado que se conserva hasta ahora.

    Returns:
        True si nuevo reemplaza a actual.
    """
    return nuevo.fecha_resultado >= actual.fecha_resultado
