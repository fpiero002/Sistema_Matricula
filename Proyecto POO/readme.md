# Sistema de Matrícula 2026-II — OTI UNSCH
> **Análisis del Caso Práctico de Programación Orientada a Objetos (POO), Diagnóstico de MRO y Rediseño con Patrón Decorador.**

---

## 📌 Contexto del Proyecto

La Oficina de Tecnologías de la Información (OTI) de la **Universidad Nacional de San Cristóbal de Huamanga (UNSCH)** desarrolló en Python el módulo de liquidación de pagos para la matrícula del semestre 2026-II.

### Reglas de Negocio
1. **Derecho Base:** Todo estudiante paga una tasa fija de **S/ 60.00**.
2. **Matrícula Extemporánea:** Recargo adicional de **S/ 15.00**.
3. **Índice Académico Desaprobatorio:** Recargo adicional de **S/ 15.00**.
4. **Beca por Violencia Sociopolítica:** Descuento del **50%** ($0.50$) sobre el monto acumulado.

### El Problema
Dos desarrolladores crearon clases combinadas mediante **Herencia Múltiple** para atender a estudiantes con las tres condiciones simultáneas:
* **Programador 1 (`Combinada1`):** Heredó en orden `(Beca, Desaprobado, Extemporanea)`.
* **Programador 2 (`Combinada2`):** Heredó en orden `(Desaprobado, Extemporanea, Beca)`.

Esto provocó que estudiantes en la misma situación administrativa (como Luis Huamaní y Rosa Ccahuana) recibieran cobros distintos (**S/ 45.00** frente a **S/ 60.00**), desencadenando reclamos hacia la OTI.

---

## 🔍 Análisis Técnico del Fallo Original

### 1. Method Resolution Order (MRO) y C3 Linearization
Python resuelve la herencia múltiple mediante el algoritmo **C3 Linearization**. Al invocar `super().calcular_costo()`, la llamada viaja de izquierda a derecha en la jerarquía del MRO.

| Versión | Cadena MRO de Resolución | Cálculo Paso a Paso | Monto Final |
| :--- | :--- | :--- | :---: |
| **Programador 1** | `Combinada1` $\rightarrow$ `Beca` $\rightarrow$ `Desaprobado` $\rightarrow$ `Extemporanea` $\rightarrow$ `Base` | Base: $60 \rightarrow +15 = 75 \rightarrow +15 = 90 \rightarrow \times 0.5$ | **S/ 45.00** |
| **Programador 2** | `Combinada2` $\rightarrow$ `Desaprobado` $\rightarrow$ `Extemporanea` $\rightarrow$ `Beca` $\rightarrow$ `Base` | Base: $60 \rightarrow \times 0.5 = 30 \rightarrow +15 = 45 \rightarrow +15$ | **S/ 60.00** |

### 2. ¿Por qué no hubo error de sintaxis?
La herencia múltiple es una característica legal del lenguaje Python. El código era **sintácticamente correcto**, pero contenía un **error de diseño arquitectónico**: las reglas financieras no son conmutativas, por lo que alterar el MRO modificó el resultado numérico.

### 3. Conflicto de Monotonicidad
Si se intenta declarar `class Combinada(MatriculaGeneral, Extemporanea):` antecediendo la clase base a su subclase, Python genera una excepción inmediata:
```text
TypeError: Cannot create a consistent method resolution order (MRO)
```
Esto ocurre porque se viola el principio de monotonicidad del algoritmo C3, el cual exige que las clases derivadas siempre antecedan a sus superclases en el orden de evaluación.

---

## 🛠️ Rediseño con Patrón Decorador (Decorator Pattern)

Para solucionar de raíz la **explosión combinatoria** y desacoplar el cálculo del orden de declaración de clases, se rediseñó el módulo utilizando el **Patrón Estructural Decorador**, promoviendo **Composición sobre Herencia**.

```
    +-------------------+
    |    IMatricula     | <-------------------+
    +-------------------+                     |
    | +calcular_monto() |                     |
    +-------------------+                     |
              ^                               |
              |                               |
    +---------+----------+                    |
    |                    |                    |
+---+---------------+  +-+--------------------+---+
| MatriculaGeneral  |  |   ModificadorMatricula   |
+-------------------+  +--------------------------+
| +calcular_monto() |  | - matricula: IMatricula  |
+-------------------+  | +calcular_monto()        |
                       +--------------------------+
                                    ^
        +---------------------------+---------------------------+
        |                           |                           |
+-------+---------------+   +-------+---------------+   +-------+---------------+
|  RecargoExtemporaneo  |   |   RecargoDesaprobado  |   |     DescuentoBeca     |
+-----------------------+   +-----------------------+   +-----------------------+
| +calcular_monto()     |   | +calcular_monto()     |   | +calcular_monto()     |
+-----------------------+   +-----------------------+   +-----------------------+
```

---

## 💻 Código de la Solución (`matricula.py`)

```python
from abc import ABC, abstractmethod

# ==========================================
# 1. INTERFAZ BASE
# ==========================================
class IMatricula(ABC):
    """
    Contrato base para todo cálculo de matrícula.
    """
    @abstractmethod
    def calcular_monto(self) -> float:
        pass


# ==========================================
# 2. COMPONENTE CONCRETO
# ==========================================
class MatriculaGeneral(IMatricula):
    """
    Monto base institucional fijado en S/ 60.00.
    """
    def calcular_monto(self) -> float:
        return 60.0


# ==========================================
# 3. DECORADOR ABSTRACTO
# ==========================================
class ModificadorMatricula(IMatricula):
    """
    Mantiene una referencia dinámica a un objeto IMatricula envuelto.
    """
    def __init__(self, matricula: IMatricula):
        self._matricula = matricula

    @abstractmethod
    def calcular_monto(self) -> float:
        return self._matricula.calcular_monto()


# ==========================================
# 4. DECORADORES CONCRETOS
# ==========================================
class RecargoExtemporaneo(ModificadorMatricula):
    """Suma un recargo de S/ 15.00 por fuera de fecha."""
    def calcular_monto(self) -> float:
        return self._matricula.calcular_monto() + 15.0


class RecargoDesaprobado(ModificadorMatricula):
    """Suma un recargo de S/ 15.00 por índice desaprobatorio."""
    def calcular_monto(self) -> float:
        return self._matricula.calcular_monto() + 15.0


class DescuentoBeca(ModificadorMatricula):
    """Aplica un descuento del 50% al monto acumulado."""
    def calcular_monto(self) -> float:
        return self._matricula.calcular_monto() * 0.5


# ==========================================
# 5. CASOS DE PRUEBA Y DEMOSTRACIÓN
# ==========================================
if __name__ == "__main__":
    print("=== SISTEMA DE MATRÍCULA OTI - UNSCH 2026-II ===\n")

    # Opción A: Acumular recargos primero y aplicar beca al total final
    estudiante_a = MatriculaGeneral()
    estudiante_a = RecargoDesaprobado(estudiante_a)
    estudiante_a = RecargoExtemporaneo(estudiante_a)
    estudiante_a = DescuentoBeca(estudiante_a)

    print(f"Estrategia A (Beca al final): S/ {estudiante_a.calcular_monto():.2f}")

    # Opción B: Aplicar beca a la base y sumar recargos después
    estudiante_b = MatriculaGeneral()
    estudiante_b = DescuentoBeca(estudiante_b)
    estudiante_b = RecargoDesaprobado(estudiante_b)
    estudiante_b = RecargoExtemporaneo(estudiante_b)

    print(f"Estrategia B (Beca al inicio): S/ {estudiante_b.calcular_monto():.2f}")
```

---

## 🚀 Cómo Ejecutar la Solución

1. **Requisitos:** Asegúrate de tener instalado Python 3.8 o superior.
2. **Ejecutar el script:**
   ```bash
   python matricula.py
   ```
3. **Salida esperada:**
   ```text
   === SISTEMA DE MATRÍCULA OTI - UNSCH 2026-II ===

   Estrategia A (Beca al final): S/ 45.00
   Estrategia B (Beca al inicio): S/ 60.00
   ```

---

## 🏆 Principios SOLID Aplicados

* **Open/Closed Principle (OCP):** Nuevas condiciones académicas (ej. *Descuento Tercio Superior*) pueden agregarse creando un nuevo decorador sin alterar el código existente.
* **Single Responsibility Principle (SRP):** Cada clase calcula únicamente la regla que le corresponde.
* **Liskov Substitution Principle (LSP):** Cualquier combinación envuelta en un decorador sigue respondiendo como un objeto `IMatricula`.