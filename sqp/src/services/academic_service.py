"""
src/services/academic_service.py
Business logic layer.


"""

from typing import List, Dict, Any, Optional
from src.models.database import get_notas, get_estudiantes, get_materias

# ========== Constantes (eliminación de magic numbers) ==========
NOTA_MINIMA_APROBACION: float = 3.0
DECIMALES_REDONDEO: int = 2


# ========== Funciones básicas ==========

def es_aprobado(nota: float) -> bool:
    """Determina si una nota es aprobada según la constante NOTA_MINIMA_APROBACION."""
    return nota >= NOTA_MINIMA_APROBACION


def _calcular_promedio(notas: List[Dict[str, Any]]) -> float:
    """
    Función genérica para calcular promedio de una lista de notas.
    
    CORRECCIÓN: Función auxiliar que elimina la duplicación de código
    entre calcular_promedio_estudiante y calcular_promedio_materia.
    
    Args:
        notas: Lista de diccionarios de notas
        
    Returns:
        Promedio redondeado o 0.0 si la lista está vacía
    """
    if not notas:
        return 0.0
    
    total = sum(n.get("valor", 0.0) for n in notas)
    return round(total / len(notas), DECIMALES_REDONDEO)


def _clasificar_notas(notas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Clasifica las notas en aprobadas y reprobadas.
    
    CORRECCIÓN: Función auxiliar para reducir la responsabilidad de reporte_academico.
    
    Returns:
        Diccionario con listas de aprobadas y reprobadas
    """
    aprobadas = [n for n in notas if es_aprobado(n["valor"])]
    reprobadas = [n for n in notas if not es_aprobado(n["valor"])]
    
    return {
        "aprobadas": aprobadas,
        "reprobadas": reprobadas,
        "total_aprobadas": len(aprobadas),
        "total_reprobadas": len(reprobadas)
    }


def _calcular_promedio_estudiante_raw(codigo: str) -> Optional[List[Dict[str, Any]]]:
    """
    Obtiene las notas de un estudiante.
    
    CORRECCIÓN: Extracción de la lógica de filtrado para reutilización.
    """
    return [n for n in get_notas() if n.get("codigo_estudiante", "").upper() == codigo.upper()]


def _calcular_promedio_materia_raw(codigo: str) -> Optional[List[Dict[str, Any]]]:
    """
    Obtiene las notas de una materia.
    
    CORRECCIÓN: Extracción de la lógica de filtrado para reutilización.
    """
    return [n for n in get_notas() if n.get("codigo_materia", "").upper() == codigo.upper()]


# ========== Funciones principales (refactorizadas) ==========

def calcular_promedio_estudiante(codigo: str) -> float:
    """
    Calcula el promedio de notas de un estudiante.
    
    CORRECCIÓN: Ahora usa la función genérica _calcular_promedio.
    CORRECCIÓN: Ya no lanza ZeroDivisionError (retorna 0.0 si no hay notas).
    """
    notas = _calcular_promedio_estudiante_raw(codigo)
    return _calcular_promedio(notas)


def calcular_promedio_materia(codigo: str) -> float:
    """
    Calcula el promedio de notas de una materia.
    
    CORRECCIÓN: Ahora usa la función genérica _calcular_promedio.
    CORRECCIÓN: Ya no lanza ZeroDivisionError (retorna 0.0 si no hay notas).
    """
    notas = _calcular_promedio_materia_raw(codigo)
    return _calcular_promedio(notas)


def reporte_academico(codigo_estudiante: str) -> Dict[str, Any]:
    """
    Genera un reporte completo de un estudiante.
    
    CORRECCIÓN: Ahora es más modular (usa _clasificar_notas).
    CORRECCIÓN: Ahora retorna materias_vistas (antes variable no usada).
    CORRECCIÓN: Mejor manejo de casos borde.
    """
    estudiantes = get_estudiantes()
    codigo_normalizado = codigo_estudiante.upper()
    
    # Validar existencia del estudiante
    if codigo_normalizado not in estudiantes:
        return {"error": "Estudiante no encontrado"}
    
    estudiante = estudiantes[codigo_normalizado]
    notas = _calcular_promedio_estudiante_raw(codigo_estudiante)
    
    # Calcular materias vistas (antes variable no usada)
    materias_vistas = {n.get("codigo_materia") for n in notas}
    
    # Clasificar notas
    clasificacion = _clasificar_notas(notas)
    
    # Calcular promedio
    promedio = _calcular_promedio(notas)
    
    return {
        "estudiante": estudiante.get("nombre", "Desconocido"),
        "codigo": codigo_normalizado,
        "total_notas": len(notas),
        "aprobadas": clasificacion["total_aprobadas"],
        "reprobadas": clasificacion["total_reprobadas"],
        "promedio": promedio,
        "materias_vistas": len(materias_vistas),  # CORRECCIÓN: Ahora se retorna
        "materias_detalle": list(materias_vistas) if materias_vistas else []  # Detalle adicional
    }


def estadisticas_globales() -> Dict[str, Any]:
    """
    Retorna estadísticas globales del sistema.
    
    CORRECCIÓN: Mejor separación de responsabilidades.
    CORRECCIÓN: Manejo seguro de división por cero.
    """
    notas = get_notas()
    estudiantes = get_estudiantes()
    materias = get_materias()
    
    # Calcular promedio global de forma segura
    promedio_global = 0.0
    if notas:
        suma_total = sum(n.get("valor", 0.0) for n in notas)
        promedio_global = round(suma_total / len(notas), DECIMALES_REDONDEO)
    
    # Calcular estadísticas adicionales útiles
    if estudiantes:
        promedios_estudiantes = [calcular_promedio_estudiante(codigo) for codigo in estudiantes.keys()]
        promedio_estudiantes = round(sum(promedios_estudiantes) / len(promedios_estudiantes), DECIMALES_REDONDEO) if promedios_estudiantes else 0.0
    else:
        promedio_estudiantes = 0.0
    
    return {
        "total_estudiantes": len(estudiantes),
        "total_materias": len(materias),
        "total_notas": len(notas),
        "promedio_global": promedio_global,
        "promedio_por_estudiante": promedio_estudiantes,  # Nueva métrica útil
        "tasa_aprobacion": _calcular_tasa_aprobacion(notas) if notas else 0.0  # Nueva métrica
    }


def _calcular_tasa_aprobacion(notas: List[Dict[str, Any]]) -> float:
    """
    Calcula el porcentaje de notas aprobadas.
    
    CORRECCIÓN: Nueva función auxiliar para métricas adicionales.
    """
    if not notas:
        return 0.0
    
    aprobadas = sum(1 for n in notas if es_aprobado(n.get("valor", 0.0)))
    return round((aprobadas / len(notas)) * 100, DECIMALES_REDONDEO)


def get_materias_con_promedio() -> Dict[str, float]:
    """
    Retorna un diccionario con todas las materias y su promedio.
    
    CORRECCIÓN: Nueva funcionalidad útil para reportes.
    """
    materias = get_materias()
    return {
        codigo: calcular_promedio_materia(codigo)
        for codigo in materias.keys()
    }


def get_estudiantes_con_promedio() -> Dict[str, float]:
    """
    Retorna un diccionario con todos los estudiantes y su promedio.
    
    CORRECCIÓN: Nueva funcionalidad útil para reportes.
    """
    estudiantes = get_estudiantes()
    return {
        codigo: calcular_promedio_estudiante(codigo)
        for codigo in estudiantes.keys()
    }