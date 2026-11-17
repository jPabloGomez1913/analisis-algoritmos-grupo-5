"""Estrategias propuestas para la lista diaria de llamadas.

Restricción del negocio: la lista contiene exactamente los k pacientes de
mayor riesgo (ninguno de menor riesgo por encima de uno de mayor riesgo que
quedó fuera) y, a igual riesgo, va primero el resultado más antiguo. Ninguna
de las dos estrategias ordena los n pendientes completos: solo se necesitan
los k primeros.
"""

import heapq

from modelo import Clave, Resultado, clave_prioridad

RIESGO_MAXIMO = 100


class _PeorPrimero:
    """Envoltorio que invierte el orden para usar heapq como montículo de máximos.

    heapq siempre deja arriba el menor elemento; al invertir la comparación,
    arriba queda el resultado de PEOR prioridad entre los guardados, que es
    el que hay que sacar cuando llega uno mejor.
    """

    __slots__ = ("clave", "resultado")

    def __init__(self, resultado: Resultado) -> None:
        self.clave: Clave = clave_prioridad(resultado)
        self.resultado = resultado

    def __lt__(self, otro: "_PeorPrimero") -> bool:
        return self.clave > otro.clave


def lista_con_monticulo(pendientes: list[Resultado], k: int) -> list[Resultado]:
    """Estrategia A: montículo (heap) de tamaño k con los mejores vistos.

    Recorre los pendientes una vez manteniendo en un montículo los k de mayor
    prioridad. La raíz es el peor de ellos: si llega uno mejor, lo reemplaza
    en O(log k). Al final se ordenan solo esos k. Tiempo O(n log k + k log k)
    y espacio O(k). Con n = 1.450.000 y k = 9.000, log k ≈ 13.

    Args:
        pendientes: resultados pendientes (no se modifican).
        k: capacidad de llamadas del día.

    Returns:
        Los k resultados de mayor prioridad, en orden de llamada.
    """
    if k <= 0:
        return []
    monticulo: list[_PeorPrimero] = []
    for resultado in pendientes:
        candidato = _PeorPrimero(resultado)
        if len(monticulo) < k:
            heapq.heappush(monticulo, candidato)
        elif candidato.clave < monticulo[0].clave:
            heapq.heapreplace(monticulo, candidato)
    return [e.resultado for e in sorted(monticulo, key=lambda e: e.clave)]


def lista_por_cubetas(pendientes: list[Resultado], k: int) -> list[Resultado]:
    """Estrategia B: cubetas por índice de riesgo (ordenamiento por conteo).

    Aprovecha que el índice de riesgo es un entero entre 0 y 100: reparte los
    pendientes en 101 cubetas en O(n), sin comparar entre sí. Luego recorre
    las cubetas de mayor a menor riesgo y solo ordena por fecha las cubetas
    que alcanzan a entrar en la lista; de la última toma únicamente los que
    faltan. Tiempo O(n + m log m), con m el tamaño de las cubetas usadas
    (m ≥ k, y en la práctica cercano a k); espacio O(n).

    Args:
        pendientes: resultados pendientes (no se modifican).
        k: capacidad de llamadas del día.

    Returns:
        Los k resultados de mayor prioridad, en orden de llamada.
    """
    cubetas: list[list[Resultado]] = [[] for _ in range(RIESGO_MAXIMO + 1)]
    for resultado in pendientes:
        cubetas[resultado.indice_riesgo].append(resultado)

    lista: list[Resultado] = []
    for riesgo in range(RIESGO_MAXIMO, -1, -1):
        faltan = k - len(lista)
        if faltan <= 0:
            break
        cubeta = cubetas[riesgo]
        if len(cubeta) <= faltan:
            lista.extend(sorted(cubeta, key=clave_prioridad))
        else:
            # Última cubeta: basta con los 'faltan' más antiguos.
            lista.extend(heapq.nsmallest(faltan, cubeta, key=clave_prioridad))
    return lista
