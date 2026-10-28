from abc import ABC, abstractmethod

# ==========================================
# 1. COMPONENTE BASE (Interfaz)
# ==========================================
class IMatricula(ABC):
    """
    Interfaz base que define el contrato para cualquier tipo de matrícula.
    Garantiza que toda matrícula o decorador implemente el método de cálculo.
    """
    @abstractmethod
    def calcular_monto(self) -> float:
        pass

# ==========================================
# 2. COMPONENTE CONCRETO
# ==========================================
class MatriculaGeneral(IMatricula):
    """
    Clase concreta principal. Representa la matrícula estándar.
    """
    def calcular_monto(self) -> float:
        # Todo estudiante paga un derecho base de S/ 60.00
        return 60.0


# ==========================================
# 3. DECORADOR BASE
# ==========================================
class ModificadorMatricula(IMatricula):
    """
    Clase abstracta Decoradora. Contiene una referencia a un objeto IMatricula
    y delega el cálculo a este componente envuelto.
    """
    def __init__(self, matricula: IMatricula):
        self._matricula = matricula

    @abstractmethod
    def calcular_monto(self) -> float:
        # Delega el cálculo al componente envuelto por defecto
        return self._matricula.calcular_monto()


# ==========================================
# 4. DECORADORES CONCRETOS (Especializaciones)
# ==========================================
class RecargoExtemporaneo(ModificadorMatricula):
    """
    Aplica el recargo de S/ 15.00 por matricularse fuera de fecha.
    """
    def calcular_monto(self) -> float:
        monto_actual = self._matricula.calcular_monto()
        return monto_actual + 15.0


class RecargoDesaprobado(ModificadorMatricula):
    """
    Aplica el recargo de S/ 15.00 por índice académico desaprobatorio.
    """
    def calcular_monto(self) -> float:
        monto_actual = self._matricula.calcular_monto()
        return monto_actual + 15.0


class DescuentoBeca(ModificadorMatricula):
    """
    Aplica un descuento del 50% al monto acumulado hasta ese momento.
    """
    def calcular_monto(self) -> float:
        monto_actual = self._matricula.calcular_monto()
        return monto_actual * 0.5


# ==========================================
# 5. CASO DE PRUEBA Y DEMOSTRACIÓN (Solución al Reclamo)
# ==========================================
if __name__ == "__main__":
    print("--- Sistema de Matrícula OTI - Semestre 2026-II ---\n")

    # Escenario A: Si la OTI decide que la beca se aplica a la base, y luego van las multas.
    # (El equivalente a lo que causó el cobro de S/ 60.00)
    estudiante_a = MatriculaGeneral()
    estudiante_a = DescuentoBeca(estudiante_a)         # 60 / 2 = 30
    estudiante_a = RecargoDesaprobado(estudiante_a)    # 30 + 15 = 45
    estudiante_a = RecargoExtemporaneo(estudiante_a)   # 45 + 15 = 60
    
    print(f"Monto Estudiante A (Beca aplicada primero): S/ {estudiante_a.calcular_monto():.2f}")

    # Escenario B: Si la OTI dictamina que los recargos se acumulan primero, y la beca cubre todo.
    # (El equivalente a lo que causó el cobro de S/ 45.00)
    estudiante_b = MatriculaGeneral()
    estudiante_b = RecargoDesaprobado(estudiante_b)    # 60 + 15 = 75
    estudiante_b = RecargoExtemporaneo(estudiante_b)   # 75 + 15 = 90
    estudiante_b = DescuentoBeca(estudiante_b)         # 90 / 2 = 45
    
    print(f"Monto Estudiante B (Beca aplicada al final): S/ {estudiante_b.calcular_monto():.2f}")