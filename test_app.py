import pytest
from app import app # Importa la instancia de la aplicación Flask desde app.py

def test_home_page():
    """
    Verifica que la ruta principal '/' funcione correctamente.
    """
    # 1. Configuración de prueba rápida (simple)
    app.config['TESTING'] = True 
    client = app.test_client()
    
    # 2. Ejecución y Comprobación
    response = client.get('/')
    
    assert response.status_code == 200
    assert b"Hola desde Flask con Traefik" in response.data # Usamos 'b' para bytes

def test_saludo_personalizado():
    """
    Verifica que la ruta '/saludo/<nombre>' retorne el saludo.
    """
    # 1. Configuración de prueba
    app.config['TESTING'] = True 
    client = app.test_client()

    # 2. Ejecución y Comprobación
    test_name = "Pedro"
    response = client.get(f'/saludo/{test_name}')
    
    assert response.status_code == 200
    
    # El contenido esperado usa el nombre de prueba y el texto fijo
    expected_text = f"Hola {test_name}, bienvenido daniela cardenas "
    assert expected_text.encode('utf-8') in response.data

def test_ruta_no_encontrada():
    """
    Verifica que una ruta inexistente retorne un código 404.
    """
    # 1. Configuración de prueba
    app.config['TESTING'] = True 
    client = app.test_client()

    # 2. Ejecución y Comprobación
    response = client.get('/esta-ruta-no-existe-nunca')
    assert response.status_code == 404