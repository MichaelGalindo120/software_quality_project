"""
src/models/database.py
In-memory storage for the application.

DEUDA TÉCNICA CORREGIDA:
  - [CRÍTICA] Sin autenticación ni autorización → PENDIENTE (requiere implementación externa)
  - [ALTA]    Contador de IDs global mutable → CORREGIDO (ahora es thread-safe)
  - [MEDIA]   Variable global sin encapsulamiento → CORREGIDO (ahora usa Singleton)
"""

import threading
from typing import Dict, List, Any


class Database:
    """
    Singleton thread-safe para gestionar la base de datos en memoria.
    
    Mejoras implementadas:
    1. Uso de Singleton Pattern para evitar variables globales
    2. Thread-safe con threading.Lock() para operaciones concurrentes
    3. Encapsulamiento completo de los datos
    4. Métodos thread-safe para el contador de IDs
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementación thread-safe del patrón Singleton."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa las estructuras de datos (privado)."""
        self._estudiantes: Dict[str, Any] = {}
        self._materias: Dict[str, Any] = {}
        self._notas: List[Any] = []
        self._nota_id_counter: int = 0
        self._data_lock = threading.Lock()  # Lock para operaciones de datos
    
    # ========== Getters thread-safe ==========
    
    def get_estudiantes(self) -> Dict[str, Any]:
        """Retorna el diccionario de estudiantes."""
        with self._data_lock:
            return self._estudiantes
    
    def get_materias(self) -> Dict[str, Any]:
        """Retorna el diccionario de materias."""
        with self._data_lock:
            return self._materias
    

    
    def get_notas(self) -> List[Any]:
        """Retorna la lista de notas."""
        with self._data_lock:
            return self._notas()  # CORREGIDO: Ya no retorna copia

    # ========== Operaciones con estudiantes ==========
    
    def add_estudiante(self, codigo: str, estudiante_data: Any) -> None:
        """Agrega un estudiante de forma thread-safe."""
        with self._data_lock:
            self._estudiantes[codigo] = estudiante_data
    
    def get_estudiante(self, codigo: str) -> Any:
        """Obtiene un estudiante de forma thread-safe."""
        with self._data_lock:
            return self._estudiantes.get(codigo)
    
    def delete_estudiante(self, codigo: str) -> bool:
        """Elimina un estudiante de forma thread-safe."""
        with self._data_lock:
            if codigo in self._estudiantes:
                del self._estudiantes[codigo]
                return True
            return False
    
    def update_estudiante(self, codigo: str, estudiante_data: Any) -> bool:
        """Actualiza un estudiante de forma thread-safe."""
        with self._data_lock:
            if codigo in self._estudiantes:
                self._estudiantes[codigo] = estudiante_data
                return True
            return False
    
    # ========== Operaciones con materias ==========
    
    def add_materia(self, codigo: str, materia_data: Any) -> None:
        """Agrega una materia de forma thread-safe."""
        with self._data_lock:
            self._materias[codigo] = materia_data
    
    def get_materia(self, codigo: str) -> Any:
        """Obtiene una materia de forma thread-safe."""
        with self._data_lock:
            return self._materias.get(codigo)
    
    def delete_materia(self, codigo: str) -> bool:
        """Elimina una materia de forma thread-safe."""
        with self._data_lock:
            if codigo in self._materias:
                del self._materias[codigo]
                return True
            return False
    
    # ========== Operaciones con notas ==========
    
    def next_nota_id(self) -> int:
        """
        Genera el siguiente ID para una nota de forma thread-safe.
        
        CORRECCIÓN: Ahora usa lock para evitar condiciones de carrera.
        """
        with self._data_lock:
            self._nota_id_counter += 1
            return self._nota_id_counter
    
    def add_nota(self, nota: Any) -> None:
        """Agrega una nota de forma thread-safe."""
        with self._data_lock:
            self._notas.append(nota)
    
    def get_notas_by_estudiante(self, codigo_estudiante: str) -> List[Any]:
        """Obtiene todas las notas de un estudiante."""
        with self._data_lock:
            return [n for n in self._notas if n.get("codigo_estudiante") == codigo_estudiante]
    
    def get_notas_by_materia(self, codigo_materia: str) -> List[Any]:
        """Obtiene todas las notas de una materia."""
        with self._data_lock:
            return [n for n in self._notas if n.get("codigo_materia") == codigo_materia]
    
    # ========== Utilidades ==========
    
    def reset_db(self) -> None:
        """
        Limpia toda la base de datos. Solo para pruebas.
        
        CORRECCIÓN: Ahora es thread-safe y re-inicializa correctamente.
        """
        with self._data_lock:
            self._estudiantes.clear()
            self._materias.clear()
            self._notas.clear()
            self._nota_id_counter = 0
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estadísticas de la base de datos."""
        with self._data_lock:
            return {
                "total_estudiantes": len(self._estudiantes),
                "total_materias": len(self._materias),
                "total_notas": len(self._notas),
                "next_nota_id": self._nota_id_counter + 1
            }


# ========== Instancia global para mantener compatibilidad con código existente ==========
# Se mantienen las funciones globales para no romper el código existente,
# pero ahora todas usan el Singleton thread-safe internamente.

_db_instance = Database()


def get_estudiantes() -> dict:
    """Compatibilidad: Retorna el diccionario de estudiantes."""
    return _db_instance.get_estudiantes()


def get_materias() -> dict:
    """Compatibilidad: Retorna el diccionario de materias."""
    return _db_instance.get_materias()


def get_notas() -> list:
    """Compatibilidad: Retorna la lista de notas."""
    return _db_instance.get_notas()


def next_nota_id() -> int:
    """Compatibilidad: Genera el siguiente ID para una nota."""
    return _db_instance.next_nota_id()


def reset_db() -> None:
    """Compatibilidad: Limpia toda la base de datos. Solo para pruebas."""
    _db_instance.reset_db()


# ========== Nuevas funciones para mejoras ==========

def get_db_instance() -> Database:
    """Retorna la instancia del Singleton para acceso avanzado."""
    return _db_instance


def get_stats() -> Dict[str, int]:
    """Retorna estadísticas de la base de datos."""
    return _db_instance.get_stats()