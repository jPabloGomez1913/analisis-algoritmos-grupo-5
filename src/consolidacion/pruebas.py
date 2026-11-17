"""Pruebas con assert de la consolidación de pacientes repetidos."""

from datos import generar_resultados
from estrategias import consolidar_con_diccionario, consolidar_ordenando
from modelo import Resultado, paciente
from regla_actual import consolidar_busqueda_lineal

ESTRATEGIAS = (consolidar_busqueda_lineal, consolidar_con_diccionario, consolidar_ordenando)


def r(tipo: str, numero: str, fecha: int, riesgo: int = 50, lote: int = 1) -> Resultado:
    """Crea un resultado de prueba con los campos que importan aquí."""
    return Resultado(tipo, numero, 1, lote, fecha, riesgo, "Municipio 001")


def normalizar(resultados: list[Resultado]) -> list[Resultado]:
    """Ordena por paciente para comparar salidas que vienen en distinto orden."""
    return sorted(resultados, key=paciente)


def cumple_restricciones(entrada: list[Resultado], salida: list[Resultado]) -> bool:
    """Verifica las restricciones del negocio sobre una consolidación.

    Exactamente un resultado por paciente, ningún paciente perdido, cada
    resultado conservado existe en la entrada y es el de fecha máxima.
    """
    pacientes_entrada = {paciente(x) for x in entrada}
    pacientes_salida = [paciente(x) for x in salida]
    if len(pacientes_salida) != len(set(pacientes_salida)):
        return False  # un paciente quedó dos veces
    if set(pacientes_salida) != pacientes_entrada:
        return False  # un paciente desapareció
    for elegido in salida:
        if elegido not in entrada:
            return False  # se inventó o modificó un registro
        fecha_max = max(x.fecha_resultado for x in entrada if paciente(x) == paciente(elegido))
        if elegido.fecha_resultado != fecha_max:
            return False  # no es el más reciente
    return True


def probar_casos_limite() -> None:
    """Entrada vacía, un solo resultado, sin repetidos y todos repetidos."""
    for estrategia in ESTRATEGIAS:
        assert estrategia([]) == []
        assert estrategia([r("CC", "1", 10)]) == [r("CC", "1", 10)]
        distintos = [r("CC", "1", 10), r("CC", "2", 5), r("TI", "1", 7)]
        assert normalizar(estrategia(distintos)) == normalizar(distintos)
        mismo = [r("CC", "9", 3), r("CC", "9", 8), r("CC", "9", 1)]
        assert estrategia(mismo) == [r("CC", "9", 8)]


def probar_tipo_documento() -> None:
    """El mismo número con distinto tipo de documento son pacientes distintos."""
    entrada = [r("CC", "100", 1), r("TI", "100", 2)]
    for estrategia in ESTRATEGIAS:
        assert len(estrategia(entrada)) == 2


def probar_mas_reciente_llega_antes() -> None:
    """Si el resultado viejo llega después, se conserva el más reciente."""
    entrada = [r("CC", "5", 100, riesgo=80), r("CC", "5", 20, riesgo=10)]
    for estrategia in ESTRATEGIAS:
        assert estrategia(entrada) == [r("CC", "5", 100, riesgo=80)]


def probar_empate_de_fecha() -> None:
    """A igual fecha, todas las estrategias conservan el último en llegar."""
    entrada = [r("CC", "7", 50, lote=1), r("CC", "7", 50, lote=2)]
    for estrategia in ESTRATEGIAS:
        assert estrategia(entrada) == [r("CC", "7", 50, lote=2)]


def probar_no_modifica_entrada() -> None:
    """Los registros originales no se modifican (trazabilidad)."""
    entrada = generar_resultados(200, semilla=1)
    copia = list(entrada)
    for estrategia in ESTRATEGIAS:
        estrategia(entrada)
        assert entrada == copia


def probar_aleatorias() -> None:
    """30 instancias: las tres estrategias coinciden y cumplen las restricciones."""
    for semilla in range(30):
        n = 50 + semilla * 20
        entrada = generar_resultados(n, semilla, tasa_repetidos=0.08 + (semilla % 8) / 100)
        referencia = normalizar(consolidar_busqueda_lineal(entrada))
        assert cumple_restricciones(entrada, referencia), semilla
        assert normalizar(consolidar_con_diccionario(entrada)) == referencia, semilla
        assert normalizar(consolidar_ordenando(entrada)) == referencia, semilla


if __name__ == "__main__":
    probar_casos_limite()
    probar_tipo_documento()
    probar_mas_reciente_llega_antes()
    probar_empate_de_fecha()
    probar_no_modifica_entrada()
    probar_aleatorias()
    print("Todas las pruebas pasaron.")
