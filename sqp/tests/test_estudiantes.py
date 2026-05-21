"""
tests/test_estudiantes.py
Pruebas unitarias para el módulo de estudiantes.
Cobertura actual: ~55% — el equipo debe completar hasta ≥85%.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from src.models.database import reset_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_db():
    """Limpia la base de datos antes de cada test."""
    reset_db()
    yield
    reset_db()


class TestCrearEstudiante:

    def test_crear_estudiante_exitoso(self):
        payload = {
            "codigo": "E001",
            "nombre": "Ana García",
            "email": "ana@test.com",
            "semestre": 5
        }
        response = client.post("/estudiantes/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["codigo"] == "E001"
        assert data["nombre"] == "Ana García"
        assert data["activo"] is True

    def test_crear_estudiante_codigo_duplicado(self):
        payload = {"codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 1}
        client.post("/estudiantes/", json=payload)
        response = client.post("/estudiantes/", json=payload)
        assert response.status_code == 400

    def test_crear_estudiante_email_invalido(self):
        payload = {"codigo": "E002", "nombre": "Pedro", "email": "sinatsign", "semestre": 2}
        response = client.post("/estudiantes/", json=payload)
        assert response.status_code == 400

    def test_crear_estudiante_semestre_invalido(self):
        payload = {"codigo": "E003", "nombre": "Luis", "email": "l@t.com", "semestre": 11}
        response = client.post("/estudiantes/", json=payload)
        assert response.status_code == 400


class TestObtenerEstudiante:

    def test_obtener_estudiante_existente(self):
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 3
        })
        response = client.get("/estudiantes/E001")
        assert response.status_code == 200
        assert response.json()["codigo"] == "E001"

    def test_obtener_estudiante_inexistente(self):
        response = client.get("/estudiantes/X999")
        assert response.status_code == 404


class TestListarEstudiantes:

    def test_listar_vacio(self):
        response = client.get("/estudiantes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_con_estudiantes(self):
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 1
        })
        response = client.get("/estudiantes/")
        assert len(response.json()) == 1

    def test_eliminar_estudiante_existente(self):
    client.post("/estudiantes/", json={...})
    response = client.delete("/estudiantes/E001")
    assert response.status_code == 204

def test_eliminar_estudiante_inexistente(self):
    response = client.delete("/estudiantes/X999")
    assert response.status_code == 404

def test_desactivar_estudiante(self):
    client.post("/estudiantes/", json={...})
    response = client.put("/estudiantes/E001/desactivar")
    assert response.status_code == 200
    assert response.json()["activo"] is False

def test_semestre_minimo_y_maximo(self):
    # semestre=1 válido
    r1 = client.post("/estudiantes/", json={"codigo":"E001",...,"semestre":1})
    assert r1.status_code == 201
    # semestre=10 válido
    r2 = client.post("/estudiantes/", json={"codigo":"E002",...,"semestre":10})
    assert r2.status_code == 201


# ─────────────────────────────────────────────────────────────
#  TODO para el equipo:
#  Agregar tests para:
#  - test_eliminar_estudiante_existente
#  - test_eliminar_estudiante_inexistente
#  - test_desactivar_estudiante
#  - test_codigo_se_convierte_a_mayusculas
#  - test_semestre_minimo_valido (semestre=1)
#  - test_semestre_maximo_valido (semestre=10)
# ─────────────────────────────────────────────────────────────
