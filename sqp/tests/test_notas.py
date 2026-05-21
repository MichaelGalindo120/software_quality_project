"""
tests/test_notas.py
Pruebas unitarias para notas y el servicio académico.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from src.models.database import reset_db
from src.services.academic_service import (
    es_aprobado, calcular_promedio_estudiante,
    reporte_academico, estadisticas_globales
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_db():
    reset_db()
    yield
    reset_db()


@pytest.fixture
def setup_datos():
    """Crea un estudiante y una materia base para las pruebas."""
    client.post("/estudiantes/", json={
        "codigo": "E001", "nombre": "Ana García",
        "email": "ana@test.com", "semestre": 5
    })
    client.post("/materias/", json={
        "codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3
    })
    yield


class TestEsAprobado:
    def test_nota_tres_es_aprobado(self):
        assert es_aprobado(3.0) is True

    def test_nota_mayor_tres_es_aprobado(self):
        assert es_aprobado(4.5) is True

    def test_nota_menor_tres_es_reprobado(self):
        assert es_aprobado(2.9) is False

    def test_nota_cero_es_reprobado(self):
        assert es_aprobado(0.0) is False


class TestRegistrarNota:
    def test_registrar_nota_exitosa(self, setup_datos):
        payload = {
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial 1",
            "valor": 4.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["valor"] == 4.0
        assert data["aprobado"] is True

    def test_registrar_nota_estudiante_inexistente(self, setup_datos):
        payload = {
            "codigo_estudiante": "X999",
            "codigo_materia": "CS101",
            "actividad": "Parcial",
            "valor": 3.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 404

    def test_registrar_nota_materia_inexistente(self, setup_datos):
        payload = {
            "codigo_estudiante": "E001",
            "codigo_materia": "XX999",
            "actividad": "Parcial",
            "valor": 3.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 404

    def test_registrar_nota_valor_invalido(self, setup_datos):
        payload = {
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial",
            "valor": 6.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 400


class TestReporteAcademico:
    def test_reporte_estudiante_inexistente(self):
        resultado = reporte_academico("X999")
        assert "error" in resultado

    def test_reporte_sin_notas(self):
        from src.models.database import get_estudiantes
        get_estudiantes()["E001"] = {
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com",
            "semestre": 1, "activo": True
        }
        resultado = reporte_academico("E001")
        assert resultado["total_notas"] == 0
        assert resultado["promedio"] == 0.0


class TestEstadisticasGlobales:
    def test_estadisticas_sin_datos(self):
        stats = estadisticas_globales()
        assert stats["total_estudiantes"] == 0
        assert stats["promedio_global"] == 0.0

    def test_division_por_cero_promedio_estudiante(self, setup_datos):
        # AHORA: No lanza excepción, retorna 0.0 (comportamiento mejorado)
        promedio = calcular_promedio_estudiante("E001")
        assert promedio == 0.0  # Sin notas, promedio es 0.0

    def test_promedio_estudiante_endpoint(self, setup_datos):
        # Primero crear un estudiante (setup_datos ya lo hace)
        # Registrar una nota
        response_nota = client.post("/notas/", json={
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "P1",
            "valor": 4.0
        })
        assert response_nota.status_code == 201
        
        response = client.get("/notas/promedio/estudiante/E001")
        assert response.status_code == 200
        assert response.json()["promedio"] == 4.0

    def test_reporte_con_notas_mixtas(self, setup_datos):
        # Registrar nota aprobada
        response1 = client.post("/notas/", json={
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial 1",
            "valor": 4.0
        })
        assert response1.status_code == 201
        
        # Registrar nota reprobada
        response2 = client.post("/notas/", json={
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial 2",
            "valor": 2.0
        })
        assert response2.status_code == 201
        
        resultado = reporte_academico("E001")
        assert resultado["total_notas"] == 2
        assert resultado["promedio"] == 3.0

    def test_notas_de_estudiante_endpoint(self, setup_datos):
        response_nota = client.post("/notas/", json={
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial 1",
            "valor": 4.0
        })
        assert response_nota.status_code == 201
        
        response = client.get("/notas/estudiante/E001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_promedio_materia_endpoint(self, setup_datos):
        response_nota = client.post("/notas/", json={
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial 1",
            "valor": 4.0
        })
        assert response_nota.status_code == 201
        
        response = client.get("/notas/promedio/materia/CS101")
        assert response.status_code == 200
        data = response.json()
        assert data["promedio"] == 4.0

    def test_estadisticas_con_datos(self, setup_datos):
        # Crear segundo estudiante
        response_est = client.post("/estudiantes/", json={
            "codigo": "E002", "nombre": "Luis",
            "email": "luis@test.com", "semestre": 3
        })
        assert response_est.status_code == 201
        
        # Nota para E001
        response1 = client.post("/notas/", json={
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "P1",
            "valor": 4.0
        })
        assert response1.status_code == 201
        
        # Nota para E002
        response2 = client.post("/notas/", json={
            "codigo_estudiante": "E002",
            "codigo_materia": "CS101",
            "actividad": "P1",
            "valor": 3.0
        })
        assert response2.status_code == 201
        
        stats = estadisticas_globales()
        assert stats["total_estudiantes"] == 2
        assert stats["total_notas"] == 2