"""Pruebas con assert de la lista diaria de llamadas."""

from datos import generar_pendientes
from estrategias import lista_con_monticulo, lista_por_cubetas
from modelo import Resultado, clave_prioridad
from regla_actual import lista_por_insercion

ESTRATEGIAS = (lista_por_insercion, lista_con_monticulo, lista_por_cubetas)


def r(numero: str, riesgo: int, fecha: int, tipo: str = "CC") -> Resultado:
    """Crea un resultado de prueba con los campos que importan aquí."""
    return Resultado(tipo, numero, 1, 1, fecha, riesgo, "Municipio 001")


def cumple_restricciones(pendientes: list[Resultado], lista: list[Resultado], k: int) -> bool:
    """Verifica las restricciones del negocio sobre una lista de llamadas.

    Tamaño min(k, n), sin repetidos, todos vienen de los pendientes, la lista
    está en orden de prioridad y ningún pendiente que quedó fuera tiene más
    prioridad que el último de la lista.
    """
    if len(lista) != min(k, len(pendientes)) or len(set(lista)) != len(lista):
        return False
    if any(x not in pendientes for x in lista):
        return False
    claves = [clave_prioridad(x) for x in lista]
    if claves != sorted(claves):
        return False  # mal ordenada (riesgo descendente, fecha ascendente)
    if lista:
        elegidos = set(lista)
        peor_elegido = claves[-1]
        if any(clave_prioridad(x) < peor_elegido for x in pendientes if x not in elegidos):
            return False  # quedó fuera alguien con más prioridad
    return True


def probar_casos_limite() -> None:
    """Sin pendientes, k = 0, k mayor que n y un solo pendiente."""
    unos = [r("1", 50, 10), r("2", 90, 5), r("3", 10, 1)]
    for estrategia in ESTRATEGIAS:
        assert estrategia([], 5) == []
        assert estrategia(unos, 0) == []
        assert estrategia(unos, 10) == [r("2", 90, 5), r("1", 50, 10), r("3", 10, 1)]
        assert estrategia([r("7", 70, 7)], 1) == [r("7", 70, 7)]


def probar_desempate_por_antiguedad() -> None:
    """A igual riesgo va primero el más antiguo, aunque haya llegado después."""
    pendientes = [r("A", 80, 300), r("B", 80, 100), r("C", 80, 200), r("D", 95, 999)]
    esperado = [r("D", 95, 999), r("B", 80, 100), r("C", 80, 200)]
    for estrategia in ESTRATEGIAS:
        assert estrategia(pendientes, 3) == esperado


def probar_corte_en_empate() -> None:
    """Si el corte de k cae dentro de un grupo de igual riesgo, entran los más antiguos."""
    pendientes = [r(str(i), 60, 100 - i) for i in range(10)] + [r("X", 99, 50)]
    for estrategia in ESTRATEGIAS:
        lista = estrategia(pendientes, 4)
        assert lista[0] == r("X", 99, 50)
        assert [x.fecha_resultado for x in lista[1:]] == [91, 92, 93]


def probar_no_modifica_entrada() -> None:
    """Los registros originales y su orden no se modifican (trazabilidad)."""
    pendientes = generar_pendientes(300, semilla=3)
    copia = list(pendientes)
    for estrategia in ESTRATEGIAS:
        estrategia(pendientes, 50)
        assert pendientes == copia


def probar_aleatorias() -> None:
    """30 instancias: las tres estrategias coinciden y cumplen las restricciones."""
    for semilla in range(30):
        n = 100 + semilla * 25
        k = max(1, n // (3 + semilla % 5))
        # La mitad de las instancias con pocas fechas posibles, para forzar empates.
        rango = 50 if semilla % 2 else 1_000_000
        pendientes = generar_pendientes(n, semilla, rango_fechas=rango)
        referencia = lista_por_insercion(pendientes, k)
        assert cumple_restricciones(pendientes, referencia, k), semilla
        assert lista_con_monticulo(pendientes, k) == referencia, semilla
        assert lista_por_cubetas(pendientes, k) == referencia, semilla


if __name__ == "__main__":
    probar_casos_limite()
    probar_desempate_por_antiguedad()
    probar_corte_en_empate()
    probar_no_modifica_entrada()
    probar_aleatorias()
    print("Todas las pruebas pasaron.")
