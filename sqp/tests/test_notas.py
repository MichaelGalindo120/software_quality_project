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
    def test_registrar_nota_exitosa(self):
        # Crear datos necesarios
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana García",
            "email": "ana@test.com", "semestre": 5
        })
        client.post("/materias/", json={
            "codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3
        })
        
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

    def test_registrar_nota_estudiante_inexistente(self):
        client.post("/materias/", json={
            "codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3
        })
        
        payload = {
            "codigo_estudiante": "X999",
            "codigo_materia": "CS101",
            "actividad": "Parcial",
            "valor": 3.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 404

    def test_registrar_nota_materia_inexistente(self):
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana García",
            "email": "ana@test.com", "semestre": 5
        })
        
        payload = {
            "codigo_estudiante": "E001",
            "codigo_materia": "XX999",
            "actividad": "Parcial",
            "valor": 3.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 404

    def test_registrar_nota_valor_invalido(self):
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana García",
            "email": "ana@test.com", "semestre": 5
        })
        client.post("/materias/", json={
            "codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3
        })
        
        payload = {
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial",
            "valor": 6.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 422


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

    def test_division_por_cero_promedio_estudiante(self):
        # Crear estudiante sin notas
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana García",
            "email": "ana@test.com", "semestre": 5
        })
        promedio = calcular_promedio_estudiante("E001")
        assert promedio == 0.0

    def test_promedio_estudiante_endpoint(self):
        # Crear datos
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana García",
            "email": "ana@test.com", "semestre": 5
        })
        client.post("/materias/", json={
            "codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3
        })
        
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

    def test_reporte_con_notas_mixtas(self):
        # Crear datos
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana García",
            "email": "ana@test.com", "semestre": 5
        })
        client.post("/materias/", json={
            "codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3
        })
        
        response1 = client.post("/notas/", json={
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial 1",
            "valor": 4.0
        })
        assert response1.status_code == 201
        
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

    def test_notas_de_estudiante_endpoint(self):
        # Crear datos
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana García",
            "email": "ana@test.com", "semestre": 5
        })
        client.post("/materias/", json={
            "codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3
        })
        
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

    def test_promedio_materia_endpoint(self):
        # Crear datos
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana García",
            "email": "ana@test.com", "semestre": 5
        })
        client.post("/materias/", json={
            "codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3
        })
        
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

    def test_estadisticas_con_datos(self):
        # Crear estudiantes
        response_est1 = client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana",
            "email": "ana@test.com", "semestre": 5
        })
        assert response_est1.status_code == 201
        
        response_est2 = client.post("/estudiantes/", json={
            "codigo": "E002", "nombre": "Luis",
            "email": "luis@test.com", "semestre": 3
        })
        assert response_est2.status_code == 201

        # Crear materia
        response_mat = client.post("/materias/", json={
            "codigo": "CS101", "nombre": "Calidad", "creditos": 3
        })
        assert response_mat.status_code == 201

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