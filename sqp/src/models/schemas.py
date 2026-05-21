"""
src/models/schemas.py
Pydantic schemas for request/response validation.
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


# ── Estudiante ────────────────────────────────────────────────

class EstudianteCreate(BaseModel):
    """Esquema para crear un nuevo estudiante."""
    
    codigo: str = Field(
        ...,
        description="Código único del estudiante (ej: E001)",
        min_length=3,
        max_length=10
    )
    nombre: str = Field(
        ...,
        description="Nombre completo del estudiante",
        min_length=2,
        max_length=100
    )
    email: str = Field(
        ...,
        description="Correo electrónico del estudiante",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    semestre: int = Field(
        ...,
        description=f"Semestre actual del estudiante ({SEMESTRE_MIN}-{SEMESTRE_MAX})",
        ge=SEMESTRE_MIN,
        le=SEMESTRE_MAX
    )
    
    # CORREGIDO: Usar ConfigDict en lugar de class Config (Pydantic V2)
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "codigo": "E001",
                "nombre": "Ana García",
                "email": "ana.garcia@universidad.edu",
                "semestre": 5
            }
        }
    )


class EstudianteResponse(BaseModel):
    """Esquema para respuesta de estudiante."""
    
    codigo: str = Field(..., description="Código único del estudiante")
    nombre: str = Field(..., description="Nombre completo del estudiante")
    email: str = Field(..., description="Correo electrónico del estudiante")
    semestre: int = Field(..., description="Semestre actual", ge=SEMESTRE_MIN, le=SEMESTRE_MAX)
    activo: bool = Field(default=True, description="Estado activo/inactivo del estudiante")
    
    model_config = ConfigDict(
        json_schema_extra={
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
    """Esquema para crear una nueva materia."""
    
    codigo: str = Field(
        ...,
        description="Código único de la materia (ej: CS101)",
        min_length=3,
        max_length=10
    )
    nombre: str = Field(
        ...,
        description="Nombre de la materia",
        min_length=3,
        max_length=100
    )
    creditos: int = Field(
        ...,
        description=f"Número de créditos ({CREDITOS_MIN}-{CREDITOS_MAX})",
        ge=CREDITOS_MIN,
        le=CREDITOS_MAX
    )
    # CORREGIDO: Reemplazar 'Any' por 'Optional[str]'
    descripcion: Optional[str] = Field(
        default=None,
        description="Descripción opcional de la materia",
        max_length=500
    )
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "codigo": "CS101",
                "nombre": "Calidad del Software",
                "creditos": 3,
                "descripcion": "Curso de calidad y pruebas de software"
            }
        }
    )


class MateriaResponse(BaseModel):
    """Esquema para respuesta de materia."""
    
    codigo: str = Field(..., description="Código único de la materia")
    nombre: str = Field(..., description="Nombre de la materia")
    creditos: int = Field(..., description="Número de créditos", ge=CREDITOS_MIN, le=CREDITOS_MAX)
    descripcion: Optional[str] = Field(default=None, description="Descripción opcional")
    
    model_config = ConfigDict(
        json_schema_extra={
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
    """Esquema para crear una nueva nota."""
    
    codigo_estudiante: str = Field(
        ...,
        description="Código del estudiante",
        min_length=3,
        max_length=10
    )
    codigo_materia: str = Field(
        ...,
        description="Código de la materia",
        min_length=3,
        max_length=10
    )
    actividad: str = Field(
        ...,
        description="Nombre de la actividad evaluada",
        min_length=3,
        max_length=100
    )
    valor: float = Field(
        ...,
        description=f"Valor de la nota ({NOTA_MIN}-{NOTA_MAX})",
        ge=NOTA_MIN,
        le=NOTA_MAX
    )
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "codigo_estudiante": "E001",
                "codigo_materia": "CS101",
                "actividad": "Examen Parcial 1",
                "valor": 4.5
            }
        }
    )


class NotaResponse(BaseModel):
    """Esquema para respuesta de nota."""
    
    id: int = Field(..., description="Identificador único de la nota")
    codigo_estudiante: str = Field(..., description="Código del estudiante")
    codigo_materia: str = Field(..., description="Código de la materia")
    actividad: str = Field(..., description="Nombre de la actividad")
    valor: float = Field(..., description="Valor de la nota", ge=NOTA_MIN, le=NOTA_MAX)
    aprobado: bool = Field(..., description="Indica si la nota es aprobada (≥3.0)")
    
    model_config = ConfigDict(
        json_schema_extra={
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