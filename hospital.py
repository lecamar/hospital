"""
Hospital - Programacion Orientada a Objetos
=======================================================

Conceptos aplicados:
- Herencia: Medico, Paciente y Enfermero heredan de Persona.
- Clases abstractas (abc): Persona, Medicamento y Examen no se pueden instanciar; obligan a las hijas a implementar ciertos mtodos.
- Polimorfismo: identificacion_individuo() y etiqueta_advertencia() se llaman igual en todos los objetos, pero cada clase responde distinto.
- Encapsulamiento: atributos privados con guion bajo (_estado, _valor...) que solo se modifican mediante @property y setters con validacion.
"""

from abc import ABC, abstractmethod


# ======================================================================
# CLASE BASE: PERSONA
# ======================================================================
class Persona(ABC):
    """Molde comun para Medico, Paciente y Enfermero (clase abstracta)."""

    def __init__(self, nombre, documento):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre no puede estar vacio.")
        if not isinstance(documento, str) or not documento.strip():
            raise ValueError("El documento no puede estar vacio.")
        self._nombre = nombre.strip()
        self._documento = documento.strip()        

    @property
    def nombre(self):
        """Nombre de la persona (solo lectura)."""
        return self._nombre

    @property
    def documento(self):
        """Documento de identidad (solo lectura)."""
        return self._documento

    @abstractmethod
    def identificacion_individuo(self):
        """Cada hija devuelve su propia identificacion (polimorfismo)."""


# ======================================================================
# EJERCICIO 1: ENFERMERO (clase hija de Persona + polimorfismo)
# ======================================================================
class Enfermero(Persona):
    TURNOS_VALIDOS = ("mañana", "tarde", "noche")

    def __init__(self, nombre, documento, turno, area):
        super().__init__(nombre, documento)
        self._turno = None
        self._area = area
        self._pacientes_asignados = []
        self.turno = turno

    @property
    def turno(self):
        return self._turno

    @turno.setter
    def turno(self, valor):
        if not isinstance(valor, str) or valor.strip().lower() not in self.TURNOS_VALIDOS:
            raise ValueError(f"Turno invalido. Opciones: {', '.join(self.TURNOS_VALIDOS)}.")
        self._turno = valor.strip().lower()

    @property
    def area(self):
        return self._area

    def registrar_ronda(self, paciente):
        if not isinstance(paciente, Paciente):
            raise TypeError("Solo se pueden registrar objetos Paciente.")
        self._pacientes_asignados.append(paciente)
        print(f"Ronda registrada: {self._nombre} atendio a {paciente.nombre} "
              f"(turno {self._turno}, area {self._area}).")

    def identificacion_individuo(self):
        return (f"Enfermero: {self._nombre} (doc. {self._documento}) - "
                f"{self._area}, turno {self._turno}")


# ======================================================================
# EJERCICIO 2: PACIENTE Y SU ESTADO RESTRINGIDO
# (tambien contiene los metodos de los ejercicios 3 y 4)
# ======================================================================
class Paciente(Persona):
    """Paciente con estado controlado, formula medica y examenes."""

    ESTADOS_VALIDOS = ("ingresado", "en tratamiento", "en recuperacion", "alta")

    def __init__(self, nombre, documento, estado="ingresado"):
        super().__init__(nombre, documento)
        self._historial_estados = []
        self._estado = None
        self._medico_tratante = None
        self._formula = []     # medicamentos recetados
        self._examenes = []    # examenes ordenados
        self.estado = estado   # pasa por el setter (valida y registra)

    # ------------------------------------------------------------------
    # EJERCICIO 2: estado restringido (setter con validacion e historial)
    # ------------------------------------------------------------------
    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, nuevo):
        if not isinstance(nuevo, str):
            # Sin esta validacion, 42.strip() lanzaria AttributeError, un error
            # confuso. TypeError describe mejor el problema real: tipo incorrecto.
            raise TypeError(
                f"El estado debe ser texto, no {type(nuevo).__name__}.")
        normalizado = nuevo.strip().lower()
        if normalizado not in self.ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado '{nuevo}' no valido. Opciones: {', '.join(self.ESTADOS_VALIDOS)}.")
        self._historial_estados.append((self._estado, normalizado))
        self._estado = normalizado

    @property
    def historial_estados(self):
        """Copia del historial: lista de tuplas (estado_anterior, estado_nuevo)."""
        return list(self._historial_estados)

    # ---- medico tratante ----
    @property
    def medico_tratante(self):
        return self._medico_tratante

    @medico_tratante.setter
    def medico_tratante(self, medico):
        if medico is not None and not isinstance(medico, Medico):
            raise TypeError("El medico tratante debe ser un objeto Medico.")
        self._medico_tratante = medico

    # ---- metodos de apoyo (los llama Medico) ----
    def agregar_medicamento(self, medicamento):
        self._formula.append(medicamento)

    def agregar_examen(self, examen):
        self._examenes.append(examen)

    @property
    def examenes(self):
        return list(self._examenes)

    # ------------------------------------------------------------------
    # EJERCICIO 3: mostrar_formula() con advertencias
    # ------------------------------------------------------------------
    def mostrar_formula(self):
        print(f"--- Formula medica de {self._nombre} ---")
        if not self._formula:
            print("  (sin medicamentos)")
        for med in self._formula:
            print(f"  - {med}")
            advertencia = med.etiqueta_advertencia()  # polimorfismo
            if advertencia:
                print(f"      ! {advertencia}")

    # ------------------------------------------------------------------
    # EJERCICIO 4: mostrar_resultados() y examenes_alterados
    # ------------------------------------------------------------------
    def mostrar_resultados(self):
        print(f"--- Examenes de {self._nombre} ---")
        if not self._examenes:
            print("  (sin examenes)")
        for ex in self._examenes:
            if ex.tiene_resultado:
                print(f"  - {ex.nombre}: {ex.valor} {ex.unidad()} -> {ex.interpretacion}")
            else:
                print(f"  - {ex.nombre}: pendiente (estado: {ex.estado})")

    @property
    def examenes_alterados(self):
        """Examenes con resultado fuera de rango; ignora los que no tienen valor."""
        return [ex for ex in self._examenes if ex.tiene_resultado and not ex.es_normal]

    def identificacion_individuo(self):
        return f"Paciente: {self._nombre} (doc. {self._documento}) - estado: {self._estado}"


# ======================================================================
# EJERCICIO 3: MEDICAMENTOS (clase abstracta + hijas)
# ======================================================================
class Medicamento(ABC):
    """Clase abstracta. No se puede crear un 'Medicamento' a secas."""

    def __init__(self, nombre, dosis):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del medicamento no puede estar vacio.")
        self._nombre = nombre.strip()
        self._dosis = dosis

    @property
    def nombre(self):
        return self._nombre

    @property
    def dosis(self):
        return self._dosis

    @abstractmethod
    def etiqueta_advertencia(self):
        """Devuelve una cadena con la advertencia del medicamento."""

    def __str__(self):
        return f"{self._nombre} ({self._dosis})"


class MedicamentoComun(Medicamento):
    """Medicamento sin datos adicionales."""

    def etiqueta_advertencia(self):
        return ""  # sin advertencia especial


class Antibiotico(Medicamento):
    """Antibiotico: requiere un numero entero positivo de dias de tratamiento."""

    def __init__(self, nombre, dosis, dias_tratamiento):
        super().__init__(nombre, dosis)
        self._dias_tratamiento = None
        self.dias_tratamiento = dias_tratamiento  # pasa por el setter

    @property
    def dias_tratamiento(self):
        return self._dias_tratamiento

    @dias_tratamiento.setter
    def dias_tratamiento(self, valor):
        # bool es subclase de int en Python, por eso se excluye explicitamente
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError("Los dias de tratamiento deben ser un entero.")
        if valor <= 0:
            raise ValueError("Los dias de tratamiento deben ser mayores que 0.")
        self._dias_tratamiento = valor

    def etiqueta_advertencia(self):
        return (f"Completar los {self._dias_tratamiento} dias "
                "aunque mejoren los sintomas")


class MedicamentoControlado(Medicamento):
    """Medicamento controlado: exige un numero de registro no vacio."""

    def __init__(self, nombre, dosis, numero_registro):
        super().__init__(nombre, dosis)
        self._numero_registro = None
        self.numero_registro = numero_registro

    @property
    def numero_registro(self):
        return self._numero_registro

    @numero_registro.setter
    def numero_registro(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El numero de registro es obligatorio y no puede estar vacio.")
        self._numero_registro = valor.strip()

    def etiqueta_advertencia(self):
        return f"Requiere receta oficial - Registro {self._numero_registro}"


# ======================================================================
# EJERCICIO 4: EXAMENES DE LABORATORIO
# ======================================================================
class Examen(ABC):
    """
    Examen de laboratorio. Ciclo de vida:
        ordenado -> muestra tomada -> resultado disponible
    """

    # Orden oficial de los estados; sirve para validar las transiciones.
    ESTADOS = ("ordenado", "muestra tomada", "resultado disponible")

    def __init__(self, paciente, medico_solicitante):
        self._nombre = type(self).__name__          # "Glucemia", "Colesterol"...
        self._paciente = paciente
        self._medico_solicitante = medico_solicitante
        self._estado = "ordenado"                   # estado inicial
        self._valor = None                          # todavia no hay resultado

    # ---- metodos abstractos: cada examen define los suyos ----
    @abstractmethod
    def rango_normal(self):
        """Devuelve la tupla (minimo, maximo) considerada normal."""

    @abstractmethod
    def unidad(self):
        """Devuelve la unidad de medida, por ejemplo 'mg/dL'."""

    # ---- atributos de solo lectura ----
    @property
    def nombre(self):
        return self._nombre

    @property
    def paciente(self):
        return self._paciente

    @property
    def medico_solicitante(self):
        return self._medico_solicitante

    # ---- estado con control de transiciones ----
    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, nuevo):
        if nuevo not in self.ESTADOS:
            raise ValueError(f"Estado invalido '{nuevo}'. Opciones: {', '.join(self.ESTADOS)}.")
        actual = self.ESTADOS.index(self._estado)
        destino = self.ESTADOS.index(nuevo)
        if destino <= actual:
            raise ValueError(f"No se puede retroceder ni repetir: '{self._estado}' -> '{nuevo}'.")
        if destino > actual + 1:
            raise ValueError(
                f"No se puede saltar pasos: '{self._estado}' -> '{nuevo}'. "
                f"El siguiente paso valido es '{self.ESTADOS[actual + 1]}'.")
        self._estado = nuevo

    # ---- valor con validacion ----
    @property
    def valor(self):
        return self._valor

    @valor.setter
    def valor(self, nuevo):
        if isinstance(nuevo, bool) or not isinstance(nuevo, (int, float)):
            raise TypeError("El resultado debe ser un numero.")
        if nuevo < 0:
            raise ValueError("El resultado no puede ser negativo.")
        if self._estado == "ordenado":
            raise ValueError("No se puede cargar un resultado: aun no se tomo la muestra.")
        if self._estado == "resultado disponible":
            raise ValueError("Este examen ya tiene un resultado cargado.")
        self._valor = nuevo
        self.estado = "resultado disponible"  # cambio automatico (usa el setter)

    # ---- propiedades de solo lectura comunes a todos los examenes ----
    @property
    def tiene_resultado(self):
        return self._valor is not None

    @property
    def es_normal(self):
        if not self.tiene_resultado:
            raise ValueError(f"El examen {self._nombre} todavia no tiene resultado.")
        minimo, maximo = self.rango_normal()
        return minimo <= self._valor <= maximo

    @property
    def interpretacion(self):
        if not self.tiene_resultado:
            raise ValueError(f"El examen {self._nombre} todavia no tiene resultado.")
        minimo, maximo = self.rango_normal()
        if self._valor < minimo:
            return "bajo"
        if self._valor > maximo:
            return "alto"
        return "normal"

    def __str__(self):
        return f"{self._nombre} [{self._estado}]"


class Glucemia(Examen):
    def rango_normal(self):
        return (70, 100)

    def unidad(self):
        return "mg/dL"


class Hemoglobina(Examen):
    def rango_normal(self):
        return (12, 16)

    def unidad(self):
        return "g/dL"


class Colesterol(Examen):
    def rango_normal(self):
        return (0, 200)

    def unidad(self):
        return "mg/dL"


# ======================================================================
# MEDICO (recetar -> ejercicio 3, ordenar_examen -> ejercicio 4)
# ======================================================================
class Medico(Persona):
    def __init__(self, nombre, documento, especialidad):
        super().__init__(nombre, documento)
        self._especialidad = especialidad
        self._pacientes = []

    @property
    def especialidad(self):
        return self._especialidad

    def asignar_paciente(self, paciente):
        """Asigna un paciente y lo deja registrado como su medico tratante."""
        if paciente not in self._pacientes:
            self._pacientes.append(paciente)
            paciente.medico_tratante = self

    def _verificar_asignacion(self, paciente):
        if paciente not in self._pacientes:
            raise ValueError(
                f"El paciente {paciente.nombre} no esta asignado al medico {self._nombre}.")

    def recetar(self, paciente, medicamento):
        self._verificar_asignacion(paciente)
        paciente.agregar_medicamento(medicamento)
        print(f"Dr. {self._nombre} receto {medicamento.nombre} a {paciente.nombre}.")

    def ordenar_examen(self, paciente, examen):
        """Misma logica que recetar(): solo para pacientes asignados."""
        self._verificar_asignacion(paciente)
        paciente.agregar_examen(examen)
        print(f"Dr. {self._nombre} ordeno {examen.nombre} a {paciente.nombre}.")

    def identificacion_individuo(self):
        return f"Medico: Dr. {self._nombre} (doc. {self._documento}) - {self._especialidad}"


# ======================================================================
# PRUEBAS
# ======================================================================
def verificar_error(tipo_error, funcion, descripcion):
    """Ejecuta 'funcion' y confirma que lance 'tipo_error'."""
    try:
        funcion()
    except tipo_error as e:
        print(f"  OK  {descripcion} -> {type(e).__name__}: {e}")
    else:
        raise AssertionError(f"FALLO: '{descripcion}' no lanzo {tipo_error.__name__}")


def prueba_ejercicio_1():
    print("\n===== EJERCICIO 1: Enfermero y polimorfismo =====")
    medico = Medico("Perry Cox", "1001", "Medicina interna")
    paciente = Paciente("Tony Soprano", "2001")
    enfermero = Enfermero("Carla Espinosa", "3001", "noche", "Urgencias")
    enfermero.registrar_ronda(paciente)

    personas = [medico, paciente, enfermero]
    for p in personas:  # un solo bucle, cada objeto responde distinto
        print(" ", p.identificacion_individuo())

    verificar_error(TypeError, lambda: Persona("Rick Grimes", "1"), "Instanciar Persona abstracta")
    verificar_error(ValueError, lambda: Enfermero("Elliot Reid", "2", "madrugada", "UCI"), "Turno invalido")


def prueba_ejercicio_2():
    print("\n===== EJERCICIO 2: Estado de Paciente =====")
    p = Paciente("Michael Scott", "2001")
    print("  Paciente:", p.nombre)
    p.estado = "En Recuperacion"
    assert p.estado == "en recuperacion"
    print("  OK  'En Recuperacion' normalizado a:", p.estado)
    p.estado = "  ALTA  "
    assert p.estado == "alta"
    print("  OK  '  ALTA  ' normalizado a:", p.estado)
    verificar_error(ValueError, lambda: setattr(p, "estado", "muerto de risa"), "'muerto de risa'")
    verificar_error(TypeError, lambda: setattr(p, "estado", 42), "Asignar el numero 42")
    print("  Historial:", p.historial_estados)


def prueba_ejercicio_3():
    print("\n===== EJERCICIO 3: Medicamentos abstractos =====")
    medico = Medico("Meredith Grey", "1001", "Cirugia general")
    paciente = Paciente("Sheldon Cooper", "2001")
    medico.asignar_paciente(paciente)
    medico.recetar(paciente, MedicamentoComun("Acetaminofen", "500 mg"))
    medico.recetar(paciente, Antibiotico("Amoxicilina", "875 mg", 7))
    medico.recetar(paciente, MedicamentoControlado("Tramadol", "50 mg", "XYZ-123"))
    paciente.mostrar_formula()

    verificar_error(TypeError, lambda: Medicamento("X", "1"), "Instanciar Medicamento abstracto")
    verificar_error(ValueError, lambda: Antibiotico("A", "1 mg", 0), "Antibiotico con 0 dias")
    verificar_error(TypeError, lambda: Antibiotico("A", "1 mg", 3.5), "Antibiotico con dias decimales")
    verificar_error(ValueError, lambda: MedicamentoControlado("C", "1 mg", "  "), "Controlado sin registro")
    otro = Paciente("Peter Griffin", "9")
    verificar_error(ValueError, lambda: medico.recetar(otro, MedicamentoComun("X", "1")),
                    "Recetar a paciente no asignado")


def prueba_ejercicio_4():
    print("\n===== EJERCICIO 4: Examenes de laboratorio =====")
    medico = Medico("Hawkeye Pierce", "1001", "Cirugia de campo")
    paciente = Paciente("Jon Snow", "2001")
    medico.asignar_paciente(paciente)

    # --- ciclo completo con un examen ---
    glu = Glucemia(paciente, medico)
    medico.ordenar_examen(paciente, glu)
    assert glu.estado == "ordenado" and not glu.tiene_resultado
    verificar_error(ValueError, lambda: setattr(glu, "valor", 90), "Cargar resultado sin tomar muestra")
    verificar_error(ValueError, lambda: setattr(glu, "estado", "resultado disponible"), "Saltar de ordenado a resultado")
    verificar_error(ValueError, lambda: glu.es_normal, "es_normal sin resultado")
    glu.estado = "muestra tomada"
    verificar_error(ValueError, lambda: setattr(glu, "valor", -5), "Valor negativo")
    verificar_error(ValueError, lambda: setattr(glu, "estado", "ordenado"), "Retroceder estado")
    glu.valor = 130
    assert glu.estado == "resultado disponible"
    print("  OK  Estado cambio solo a:", glu.estado)
    assert glu.interpretacion == "alto" and not glu.es_normal

    # --- tres examenes al mismo paciente ---
    hemo = Hemoglobina(paciente, medico)
    colest = Colesterol(paciente, medico)
    medico.ordenar_examen(paciente, hemo)
    medico.ordenar_examen(paciente, colest)
    for ex in (hemo, colest):
        ex.estado = "muestra tomada"
    hemo.valor = 9.5     # bajo -> alterado
    colest.valor = 180   # normal

    paciente.mostrar_resultados()
    alterados = [e.nombre for e in paciente.examenes_alterados]
    print("  Alterados:", alterados)
    assert alterados == ["Glucemia", "Hemoglobina"]
    assert hemo.interpretacion == "bajo" and colest.interpretacion == "normal"

    # un examen pendiente no debe romper examenes_alterados
    medico.ordenar_examen(paciente, Glucemia(paciente, medico))
    assert len(paciente.examenes_alterados) == 2
    print("  OK  examenes_alterados ignora los examenes sin valor")

    verificar_error(TypeError, lambda: Examen(paciente, medico), "Instanciar Examen abstracto")
    otro = Paciente("Daenerys Targaryen", "9")
    verificar_error(ValueError, lambda: medico.ordenar_examen(otro, Glucemia(otro, medico)),
                    "Ordenar examen a paciente no asignado")


if __name__ == "__main__":
    prueba_ejercicio_1()
    prueba_ejercicio_2()
    prueba_ejercicio_3()
    prueba_ejercicio_4()
    print("\nTodas las pruebas pasaron correctamente.")