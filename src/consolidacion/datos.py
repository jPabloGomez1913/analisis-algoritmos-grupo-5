"""Generador de resultados sintéticos con pacientes repetidos y semilla fija."""

import random

from modelo import Resultado

TIPOS_DOCUMENTO = ("CC", "TI", "CE")
MUNICIPIOS = tuple(f"Municipio {i:03d}" for i in range(1, 126))
MINUTOS_TRES_ANIOS = 3 * 365 * 24 * 60


def generar_resultados(n: int, semilla: int, tasa_repetidos: float = 0.12) -> list[Resultado]:
    """Genera n resultados en orden de llegada, con pacientes repetidos.

    Una fracción tasa_repetidos de los resultados (el caso indica entre 8 % y
    15 %) corresponde a un paciente que ya tiene otro resultado. Las fechas
    son aleatorias, así que un resultado repetido puede ser más antiguo o más
    reciente que el que ya existe.

    Args:
        n: número de resultados.
        semilla: semilla del generador, para reproducir la instancia.
        tasa_repetidos: fracción de resultados de pacientes ya existentes.

    Returns:
        Lista de resultados en orden de llegada.
    """
    azar = random.Random(semilla)
    pacientes: list[tuple[str, str]] = []
    resultados: list[Resultado] = []
    for _ in range(n):
        if pacientes and azar.random() < tasa_repetidos:
            tipo, numero = azar.choice(pacientes)
        else:
            tipo = azar.choice(TIPOS_DOCUMENTO)
            numero = str(azar.randint(1_000_000, 1_999_999_999))
            pacientes.append((tipo, numero))
        resultados.append(
            Resultado(
                tipo_documento=tipo,
                numero_documento=numero,
                id_laboratorio=azar.randint(1, 290),
                id_lote=azar.randint(1, 33_000),
                fecha_resultado=azar.randint(0, MINUTOS_TRES_ANIOS),
                indice_riesgo=azar.randint(0, 100),
                municipio=azar.choice(MUNICIPIOS),
            )
        )
    return resultados
