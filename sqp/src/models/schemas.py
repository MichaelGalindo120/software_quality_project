"""
src/models/schemas.py
Pydantic schemas for request/response validation.

MEJORAS IMPLEMENTADAS:
  - [CORREGIDO] Campos con descripción usando Field()
  - [CORREGIDO] ConfigDict en lugar de class Config (Pydantic V2)
  - [CORREGIDO] Tipos Optional[str] en lugar de Any
  - [CORREGIDO] Constantes para valores mágicos
  - [MEJORADO] Validaciones de rango con ge/le
  - [MEJORADO] Validación de email con pattern
  - [MEJORADO] Ejemplos en JSON Schema
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ── Constantes para validaciones ──────────────────────────────

SEMESTRE_MIN = 1
SEMESTRE_MAX = 10
CREDITOS_MIN = 1
CREDITOS_MAX = 6
NOTA_MIN = 0.0
NOTA_MAX = 5.0
NOTA_APROBACION = 3.0
CODIGO_MIN_LENGTH = 3
CODIGO_MAX_LENGTH = 10
NOMBRE_MIN_LENGTH = 2
NOMBRE_MAX_LENGTH = 100
ACTIVIDAD_MIN_LENGTH = 3
ACTIVIDAD_MAX_LENGTH = 100
DESCRIPCION_MAX_LENGTH = 500


# ── Estudiante ────────────────────────────────────────────────

class EstudianteCreate(BaseModel):
    """
    Esquema para crear un nuevo estudiante.
    
    Valida que:
    - El código tenga entre 3 y 10 caracteres
    - El nombre tenga entre 2 y 100 caracteres
    - El email tenga formato válido
    - El semestre esté entre 1 y 10
    """
    
    codigo: str = Field(
        ...,
        description="Código único del estudiante (ej: E001)",
        min_length=CODIGO_MIN_LENGTH,
        max_length=CODIGO_MAX_LENGTH,
        example="E001"
    )
    
    nombre: str = Field(
        ...,
        description="Nombre completo del estudiante",
        min_length=NOMBRE_MIN_LENGTH,
        max_length=NOMBRE_MAX_LENGTH,
        example="Ana García"
    )
    
    email: str = Field(
        ...,
        description="Correo electrónico del estudiante",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        example="ana.garcia@universidad.edu"
    )
    
    semestre: int = Field(
        ...,
        description=f"Semestre actual del estudiante ({SEMESTRE_MIN}-{SEMESTRE_MAX})",
        ge=SEMESTRE_MIN,
        le=SEMESTRE_MAX,
        example=5
    )
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "title": "EstudianteCreate",
            "description": "Esquema para crear un nuevo estudiante"
        }
    )


class EstudianteResponse(BaseModel):
    """
    Esquema para respuesta de estudiante.
    Incluye todos los campos del estudiante más el estado activo.
    """
    
    codigo: str = Field(
        ...,
        description="Código único del estudiante",
        example="E001"
    )
    
    nombre: str = Field(
        ...,
        description="Nombre completo del estudiante",
        example="Ana García"
    )
    
    email: str = Field(
        ...,
        description="Correo electrónico del estudiante",
        example="ana.garcia@universidad.edu"
    )
    
    semestre: int = Field(
        ...,
        description=f"Semestre actual ({SEMESTRE_MIN}-{SEMESTRE_MAX})",
        ge=SEMESTRE_MIN,
        le=SEMESTRE_MAX,
        example=5
    )
    
    activo: bool = Field(
        default=True,
        description="Estado activo/inactivo del estudiante",
        example=True
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "title": "EstudianteResponse",
            "description": "Esquema de respuesta para estudiante",
            "example": {
                "codigo": "E001",
                "nombre": "Ana García",
                "email": "ana.garcia@universidad.edu",
                "semestre": 5,
                "activo": True
            }
        }
    )


# ── Materia ───────────────────────────────────────────────────

class MateriaCreate(BaseModel):
    """
    Esquema para crear una nueva materia.
    
    Valida que:
    - El código tenga entre 3 y 10 caracteres
    - El nombre tenga entre 3 y 100 caracteres
    - Los créditos estén entre 1 y 6
    """
    
    codigo: str = Field(
        ...,
        description="Código único de la materia (ej: CS101)",
        min_length=CODIGO_MIN_LENGTH,
        max_length=CODIGO_MAX_LENGTH,
        example="CS101"
    )
    
    nombre: str = Field(
        ...,
        description="Nombre de la materia",
        min_length=3,
        max_length=100,
        example="Calidad del Software"
    )
    
    creditos: int = Field(
        ...,
        description=f"Número de créditos ({CREDITOS_MIN}-{CREDITOS_MAX})",
        ge=CREDITOS_MIN,
        le=CREDITOS_MAX,
        example=3
    )
    
    descripcion: Optional[str] = Field(
        default=None,
        description="Descripción opcional de la materia",
        max_length=DESCRIPCION_MAX_LENGTH,
        example="Curso de calidad y pruebas de software"
    )
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "title": "MateriaCreate",
            "description": "Esquema para crear una nueva materia"
        }
    )


class MateriaResponse(BaseModel):
    """
    Esquema para respuesta de materia.
    Incluye todos los campos de la materia.
    """
    
    codigo: str = Field(
        ...,
        description="Código único de la materia",
        example="CS101"
    )
    
    nombre: str = Field(
        ...,
        description="Nombre de la materia",
        example="Calidad del Software"
    )
    
    creditos: int = Field(
        ...,
        description=f"Número de créditos ({CREDITOS_MIN}-{CREDITOS_MAX})",
        ge=CREDITOS_MIN,
        le=CREDITOS_MAX,
        example=3
    )
    
    descripcion: Optional[str] = Field(
        default=None,
        description="Descripción opcional",
        example="Curso de calidad y pruebas de software"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "title": "MateriaResponse",
            "description": "Esquema de respuesta para materia",
            "example": {
                "codigo": "CS101",
                "nombre": "Calidad del Software",
                "creditos": 3,
                "descripcion": "Curso de calidad y pruebas de software"
            }
        }
    )


# ── Nota ──────────────────────────────────────────────────────

class NotaCreate(BaseModel):
    """
    Esquema para crear una nueva nota.
    
    Valida que:
    - El código del estudiante tenga formato válido
    - El código de la materia tenga formato válido
    - La actividad tenga entre 3 y 100 caracteres
    - La nota esté entre 0.0 y 5.0
    """
    
    codigo_estudiante: str = Field(
        ...,
        description="Código del estudiante",
        min_length=CODIGO_MIN_LENGTH,
        max_length=CODIGO_MAX_LENGTH,
        example="E001"
    )
    
    codigo_materia: str = Field(
        ...,
        description="Código de la materia",
        min_length=CODIGO_MIN_LENGTH,
        max_length=CODIGO_MAX_LENGTH,
        example="CS101"
    )
    
    actividad: str = Field(
        ...,
        description="Nombre de la actividad evaluada",
        min_length=ACTIVIDAD_MIN_LENGTH,
        max_length=ACTIVIDAD_MAX_LENGTH,
        example="Examen Parcial 1"
    )
    
    valor: float = Field(
        ...,
        description=f"Valor de la nota ({NOTA_MIN}-{NOTA_MAX})",
        ge=NOTA_MIN,
        le=NOTA_MAX,
        example=4.5
    )
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "title": "NotaCreate",
            "description": "Esquema para crear una nueva nota"
        }
    )


class NotaResponse(BaseModel):
    """
    Esquema para respuesta de nota.
    Incluye ID auto-generado y estado de aprobación.
    """
    
    id: int = Field(
        ...,
        description="Identificador único de la nota (auto-generado)",
        ge=1,
        example=1
    )
    
    codigo_estudiante: str = Field(
        ...,
        description="Código del estudiante",
        example="E001"
    )
    
    codigo_materia: str = Field(
        ...,
        description="Código de la materia",
        example="CS101"
    )
    
    actividad: str = Field(
        ...,
        description="Nombre de la actividad",
        example="Examen Parcial 1"
    )
    
    valor: float = Field(
        ...,
        description=f"Valor de la nota ({NOTA_MIN}-{NOTA_MAX})",
        ge=NOTA_MIN,
        le=NOTA_MAX,
        example=4.5
    )
    
    aprobado: bool = Field(
        ...,
        description=f"Indica si la nota es aprobada (≥{NOTA_APROBACION})",
        example=True
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "title": "NotaResponse",
            "description": "Esquema de respuesta para nota",
            "example": {
                "id": 1,
                "codigo_estudiante": "E001",
                "codigo_materia": "CS101",
                "actividad": "Examen Parcial 1",
                "valor": 4.5,
                "aprobado": True
            }
        }
    )