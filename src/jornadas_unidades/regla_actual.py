"""Regla actual del coordinador: orden de llegada, rechazando cruces."""

from estrategia import Jornada


def asignar_por_llegada(solicitudes: list[Jornada]) -> list[Jornada]:
    """Reproduce el procedimiento actual: orden de llegada, rechazando cruces.

    No reordena las solicitudes. Acepta cada una que no se cruce con ninguna
    ya aceptada (con intervalos [inicio, fin)).

    Args:
        solicitudes: solicitudes en el orden en que llegaron.

    Returns:
        Las jornadas aceptadas, ordenadas por hora de inicio.
    """
    aceptadas: list[Jornada] = []
    for inicio, fin, pacientes in solicitudes:
        if all(fin <= a[0] or inicio >= a[1] for a in aceptadas):
            aceptadas.append((inicio, fin, pacientes))
    return sorted(aceptadas, key=lambda j: (j[0], j[1]))
