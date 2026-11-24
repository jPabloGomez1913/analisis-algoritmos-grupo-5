"""Estrategias propuestas para consolidar los pacientes repetidos.

- Estrategia A, tabla hash
- Estrategia B, lista enlazada simple
"""

from modelo import Paciente, Resultado, es_mas_reciente, paciente

def es_primo(number: int) -> bool:
    """Calcula si un número n es primo, retorna True si es primo, False sí no.

    Args:
        number (int): número a evaluar.

    Returns:
        bool: True si n es primo. False sí no es primo.
    """    
    if number < 2: return False
    
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False

    return True

def calcular_m(number: int) -> int:
    """Calcula un m que sea el primo más cercano a n/2.

    Args:
        number (int): cantidad de guías que van en la tabla hash.

    Returns:
        int: valor de m para la tabla hash.
    """    
    objetivo = number // 2
    distancia = 0
    
    while True:
        inferior = objetivo - distancia
        superior = objetivo + distancia

        if es_primo(inferior):
            return inferior

        if es_primo(superior):
            return superior

        distancia += 1

# Estrategia A: tabla hash indexada por paciente
class TablaHashPacientes:
    """Tabla hash con encadenamiento separado: paciente -> resultado vigente."""

    def __init__(self, n: int) -> None:
        """Crea una tabla vacía con m casillas, m = primo más cercano a n / 2.

        Args:
            n: cantidad de elementos que se van a guardar en la tabla.
        """
        self._casillas: list[list[int]] = [[] for _ in range(calcular_m(n))]
        self._llaves: list[Paciente] = []
        self._resultados: list[Resultado] = []

    def __len__(self) -> int:
        """Número de pacientes distintos almacenados.
        
        Returns:
            Cantidad de pacientes distintos en la tabla.            
        """
        
        return len(self._llaves)

    def posicion(self, llave: Paciente) -> int:
        """Función hash: convierte la llave en el índice de una casilla.

        Usa el hash de la tupla (tipo_documento, numero_documento) y lo
        reduce al rango de casillas con el residuo de dividir entre m.

        Args:
            llave: identificación del paciente.

        Returns:
            Índice de la casilla entre 0 y m - 1.
        """
        return hash(llave) % len(self._casillas)

    def buscar(self, llave: Paciente) -> int | None:
        """Busca al paciente recorriendo solo su casilla.

        Args:
            llave: identificación del paciente.

        Returns:
            La posición del paciente en las entradas, o None si no existe.
        """
        for indice in self._casillas[self.posicion(llave)]:
            if self._llaves[indice] == llave:
                return indice
        return None

    def registrar(self, resultado: Resultado) -> None:
        """Agrega el resultado o reemplaza el del paciente si es más reciente.

        Args:
            resultado: resultado que llega en el orden de entrada.
        """
        llave = paciente(resultado)
        indice = self.buscar(llave)
        if indice is not None:
            if es_mas_reciente(resultado, self._resultados[indice]):
                self._resultados[indice] = resultado
            return
        self._llaves.append(llave)
        self._resultados.append(resultado)
        self._casillas[self.posicion(llave)].append(len(self._llaves) - 1)

    def resultados(self) -> list[Resultado]:
        """Devuelve el resultado vigente de cada paciente.

        Returns:
            Un resultado por paciente, en orden de primera aparición.
        """
        return list(self._resultados)


def consolidar_con_tabla_hash(resultados: list[Resultado]) -> list[Resultado]:
    """Estrategia A: consolidar con una tabla hash indexada por paciente.

    Crea la tabla con n = número de resultados, de modo que tiene m ≈ n / 2
    casillas y el factor de carga (pacientes / m) nunca pasa de 2.

    Args:
        resultados: resultados en el orden en que llegaron (no se modifican).

    Returns:
        Un resultado por paciente, el más reciente, en orden de primera
        aparición del paciente (el mismo orden que la regla actual).
    """
    tabla = TablaHashPacientes(len(resultados))
    for resultado in resultados:
        tabla.registrar(resultado)
    return tabla.resultados()

# Estrategia B: lista enlazada simple de pacientes
class NodoLista:
    """Nodo de la lista: un paciente, su resultado vigente y el siguiente nodo."""

    def __init__(self, llave: Paciente, resultado: Resultado) -> None:
        """Crea un nodo sin sucesor.

        Args:
            llave: identificación del paciente.
            resultado: resultado vigente del paciente.
        """
        self.llave = llave
        self.resultado = resultado
        self.siguiente: NodoLista | None = None


class ListaEnlazadaPacientes:
    """Lista enlazada simple: paciente -> resultado vigente."""

    def __init__(self) -> None:
        """Crea una lista vacía."""
        self._cabeza: NodoLista | None = None
        self._cola: NodoLista | None = None
        self._tamanio = 0

    def __len__(self) -> int:
        """Número de pacientes distintos almacenados."""
        return self._tamanio

    def buscar(self, llave: Paciente) -> NodoLista | None:
        """Busca al paciente recorriendo la lista desde la cabeza.

        Args:
            llave: identificación del paciente.

        Returns:
            El nodo del paciente, o None si no está en la lista.
        """
        actual = self._cabeza
        while actual is not None:
            if actual.llave == llave:
                return actual
            actual = actual.siguiente
        return None

    def _agregar_al_final(self, llave: Paciente, resultado: Resultado) -> None:
        """Enlaza un nodo nuevo después de la cola, en O(1).

        Args:
            llave: identificación del paciente.
            resultado: resultado del paciente.
        """
        nuevo = NodoLista(llave, resultado)
        if self._cola is None:
            self._cabeza = nuevo
        else:
            self._cola.siguiente = nuevo
        self._cola = nuevo
        self._tamanio += 1

    def registrar(self, resultado: Resultado) -> None:
        """Agrega el resultado o reemplaza el del paciente si es más reciente.

        Args:
            resultado: resultado que llega en el orden de entrada.
        """
        llave = paciente(resultado)
        nodo = self.buscar(llave)
        if nodo is None:
            self._agregar_al_final(llave, resultado)
        elif es_mas_reciente(resultado, nodo.resultado):
            nodo.resultado = resultado

    def resultados(self) -> list[Resultado]:
        """Recorre la lista de la cabeza a la cola y reúne los resultados.

        Returns:
            El resultado vigente de cada paciente, en orden de primera
            aparición.
        """
        salida: list[Resultado] = []
        actual = self._cabeza
        while actual is not None:
            salida.append(actual.resultado)
            actual = actual.siguiente
        return salida


def consolidar_con_lista_enlazada(resultados: list[Resultado]) -> list[Resultado]:
    """Estrategia B: consolidar con una lista enlazada simple de pacientes.

    Por cada resultado recorre la lista buscando al paciente: si lo
    encuentra conserva el más reciente y, si no, lo enlaza al final.

    Args:
        resultados: resultados en el orden en que llegaron (no se modifican).

    Returns:
        Un resultado por paciente, el más reciente, en orden de primera
        aparición del paciente (el mismo orden que la regla actual).
    """
    lista = ListaEnlazadaPacientes()
    for resultado in resultados:
        lista.registrar(resultado)
    return lista.resultados()
