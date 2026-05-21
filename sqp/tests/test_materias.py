"""
tests/test_materias.py
Pruebas unitarias para el módulo de materias.
Cobertura actual: ~50% — el equipo debe completar hasta ≥85%.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from src.models.database import reset_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_db():
    reset_db()
    yield
    reset_db()


class TestCrearMateria:

    def test_crear_materia_exitosa(self):
        payload = {"codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3}
        response = client.post("/materias/", json=payload)
        assert response.status_code == 201
        assert response.json()["codigo"] == "CS101"

    def test_crear_materia_creditos_invalidos(self):
        payload = {"codigo": "CS101", "nombre": "Materia", "creditos": 0}
        response = client.post("/materias/", json=payload)
        assert response.status_code == 422  # Cambiado de 400 a 422

    def test_crear_materia_duplicada(self):
        payload = {"codigo": "CS101", "nombre": "Materia", "creditos": 3}
        client.post("/materias/", json=payload)
        response = client.post("/materias/", json=payload)
        assert response.status_code == 400


class TestObtenerMateria:

    def test_obtener_materia_existente(self):
        client.post("/materias/", json={"codigo": "CS101", "nombre": "Calidad", "creditos": 3})
        response = client.get("/materias/CS101")
        assert response.status_code == 200

    def test_obtener_materia_inexistente(self):
        response = client.get("/materias/XX999")
        assert response.status_code == 404


# ─────────────────────────────────────────────────────────────
#  TODO para el equipo:
#  Agregar tests para:
#  - test_listar_materias_vacio
#  - test_listar_materias_con_datos
#  - test_eliminar_materia_existente
#  - test_eliminar_materia_inexistente
#  - test_crear_materia_con_descripcion
#  - test_creditos_maximo_valido (creditos=6)
#  - test_codigo_se_convierte_a_mayusculas
# ─────────────────────────────────────────────────────────────
