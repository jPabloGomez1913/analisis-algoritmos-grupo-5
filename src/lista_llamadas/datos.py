"""Generador de resultados pendientes sintéticos con semilla fija."""

import random

from modelo import Resultado

TIPOS_DOCUMENTO = ("CC", "TI", "CE")
MUNICIPIOS = tuple(f"Municipio {i:03d}" for i in range(1, 126))
MINUTOS_TRES_ANIOS = 3 * 365 * 24 * 60


def generar_pendientes(n: int, semilla: int, rango_fechas: int = MINUTOS_TRES_ANIOS) -> list[Resultado]:
    """Genera n resultados pendientes, uno por paciente (ya consolidados).

    El índice de riesgo es un entero entre 0 y 100, así que con n grande hay
    muchos empates de riesgo, que es justo lo que pone a prueba el criterio
    de desempate por fecha. Un rango_fechas pequeño fuerza también empates de
    fecha.

    Args:
        n: número de resultados pendientes.
        semilla: semilla del generador, para reproducir la instancia.
        rango_fechas: amplitud, en minutos, del rango de fechas.

    Returns:
        Lista de resultados pendientes.
    """
    azar = random.Random(semilla)
    numeros = azar.sample(range(1_000_000, 1_999_999_999), n)
    return [
        Resultado(
            tipo_documento=azar.choice(TIPOS_DOCUMENTO),
            numero_documento=str(numero),
            id_laboratorio=azar.randint(1, 290),
            id_lote=azar.randint(1, 33_000),
            fecha_resultado=azar.randint(0, rango_fechas),
            indice_riesgo=azar.randint(0, 100),
            municipio=azar.choice(MUNICIPIOS),
        )
        for numero in numeros
    ]
