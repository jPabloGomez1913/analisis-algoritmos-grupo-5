"""Pruebas con assert de la operación de jornadas de la unidad móvil."""

from datos import generar_instancia
from estrategia import hay_cruce, seleccionar_jornadas, valor
from exhaustivo import seleccionar_exhaustivo
from regla_actual import asignar_por_llegada


def probar_casos_limite() -> None:
    """Verifica entrada vacía, un elemento, nada se cruza y todo se cruza."""
    assert seleccionar_jornadas([]) == []
    assert seleccionar_exhaustivo([]) == []
    assert asignar_por_llegada([]) == []
    assert seleccionar_jornadas([(60, 120, 5)]) == [(60, 120, 5)]
    assert seleccionar_exhaustivo([(60, 120, 5)]) == [(60, 120, 5)]
    assert asignar_por_llegada([(60, 120, 5)]) == [(60, 120, 5)]

    sin_cruces = [(300, 360, 2), (0, 60, 1), (120, 180, 3)]
    assert len(seleccionar_jornadas(sin_cruces)) == 3
    assert len(seleccionar_exhaustivo(sin_cruces)) == 3

    todo_cruza = [(0, 100, 1), (10, 90, 2), (50, 150, 3)]
    assert len(seleccionar_jornadas(todo_cruza)) == 1
    assert len(seleccionar_exhaustivo(todo_cruza)) == 1
    assert len(asignar_por_llegada(todo_cruza)) == 1


def probar_hay_cruce() -> None:
    """Verifica hay_cruce, incluido el borde [inicio, fin)."""
    assert hay_cruce([]) is False
    assert hay_cruce([(0, 10, 1)]) is False
    assert hay_cruce([(0, 10, 1), (10, 20, 1)]) is False  # se tocan: no cruza
    assert hay_cruce([(0, 10, 1), (9, 20, 1)]) is True
    assert hay_cruce([(0, 100, 1), (10, 20, 1)]) is True  # contenida
    assert hay_cruce([(50, 60, 1), (0, 10, 1), (5, 8, 1)]) is True


def probar_ejemplo_a_mano() -> None:
    """Verifica el ejemplo de seis jornadas resuelto a mano (2 h cada una)."""
    ejemplo = [
        (480, 600, 5), (540, 660, 5), (600, 720, 5),
        (660, 780, 5), (720, 840, 5), (780, 900, 5),
    ]
    esperado = [(480, 600, 5), (600, 720, 5), (720, 840, 5)]
    assert seleccionar_jornadas(ejemplo) == esperado
    assert valor(seleccionar_exhaustivo(ejemplo)) == 3


def probar_aleatorias() -> None:
    """Verifica 30 instancias aleatorias: estrategia == exhaustiva y sin cruces."""
    for semilla in range(30):
        n = 6 + semilla % 7  # entre 6 y 12 solicitudes
        instancia = generar_instancia(n, semilla)
        voraz = seleccionar_jornadas(instancia)
        exacto = seleccionar_exhaustivo(instancia)
        assert valor(voraz) == valor(exacto), (semilla, instancia)
        # Restricción del negocio: ninguna unidad con jornadas cruzadas.
        assert not hay_cruce(voraz)
        assert not hay_cruce(exacto)
        assert not hay_cruce(asignar_por_llegada(instancia))
        # Todo lo elegido viene de las solicitudes y la regla actual no la supera.
        assert all(j in instancia for j in voraz)
        assert valor(asignar_por_llegada(instancia)) <= valor(voraz)


def probar_contraejemplo() -> None:
    """Verifica la instancia donde la regla actual es peor que la estrategia."""
    instancia = [
        (480, 960, 30),  # A, llega primero
        (480, 600, 5),   # B
        (600, 720, 5),   # C
        (720, 840, 5),   # D
        (840, 960, 5),   # E
    ]
    actual = asignar_por_llegada(instancia)
    optimo = seleccionar_jornadas(instancia)
    assert actual == [(480, 960, 30)]
    assert len(optimo) == 4
    assert len(actual) < len(optimo)
    assert len(optimo) - len(actual) == 3
    assert valor(seleccionar_exhaustivo(instancia)) == 4


if __name__ == "__main__":
    probar_casos_limite()
    probar_hay_cruce()
    probar_ejemplo_a_mano()
    probar_aleatorias()
    probar_contraejemplo()
    print("Todas las pruebas pasaron.")
