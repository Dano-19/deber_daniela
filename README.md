#  CI/CD para Aplicación Flask con Docker y GitHub Actions

Este repositorio sirve como ejemplo práctico para demostrar el ciclo de Integración Continua (CI) y Entrega Continua (CD) hasta la fase de **Construcción del Paquete (Package)**, utilizando una aplicación web simple de **Flask**, contenedores **Docker** y **GitHub Actions** como orquestador del pipeline.

---

## 1. Concepto y Ciclo de CI/CD

El ciclo de **CI/CD** (Integración Continua / Entrega Continua o Despliegue Continuo) es una práctica fundamental en DevOps que permite automatizar los pasos desde el desarrollo del código hasta la entrega o despliegue en un entorno de producción.

### Integración Continua (CI)

La CI se enfoca en fusionar los cambios de código de múltiples desarrolladores en una rama principal de forma continua. Sus pasos clave son:

- **Commit del Código:** El desarrollador sube los cambios.
- **Build (Compilación):** Se prepara el código para la ejecución (en este caso, instalando dependencias).
- **Pruebas (Testing):** Se ejecutan pruebas automáticas para asegurar que el nuevo código no rompa funcionalidades existentes.

### Entrega Continua (CD)

La CD extiende la CI. Una vez que el código pasa todas las pruebas, se automatiza la preparación y la entrega.

- **Construcción del Package/Artefacto:** Se crea un paquete ejecutable (artefacto) que contiene todo lo necesario para correr la aplicación. En este ejemplo, es una **Imagen Docker**.
- **Almacenamiento (Registry):** El artefacto se publica en un registro (como Docker Hub o GitHub Container Registry).
- **Despliegue (Deployment):** El artefacto puede ser desplegado automáticamente en un entorno de staging o producción.

---

## 2. Ejemplo Práctico: Pipeline de GitHub Actions

El archivo de flujo de trabajo (`.github/workflows/daniela.yml`) define un pipeline que se activa automáticamente con cada push a la rama `main`. Este pipeline implementa los pasos de CI/CD hasta la publicación del paquete (Docker Image).

### 2.1. El Workflow (`.github/workflows/daniela.yml`)

| Paso del Pipeline | Etapa de CI/CD | Descripción y Archivos Involucrados | Cumplimiento (Rúbrica) |
| :--- | :--- | :--- | :--- |
| **Checkout repository** | CI | Obtiene el código fuente del repositorio. | - |
| **Install dependencies** | CI (Build) | Instala las dependencias de Python listadas en `requirements.txt`. | CI/CD Configuración |
| **Run tests** | CI (Testing) | Ejecuta `pytest` para correr las pruebas unitarias definidas en `test_app.py`. | Pruebas |
| **Login to GitHub Container Registry** | CD (Preparación) | Se autentica en `ghcr.io` usando el `GITHUB_TOKEN`. | - |
| **Build and push Docker image** | CD (Package) | Construye la Imagen Docker (usando Dockerfile) y la sube a `ghcr.io` (Registro de Contenedores de GitHub). | Construcción del package |

### 2.2. La Aplicación (Flask)

El archivo `app.py` contiene la lógica de la aplicación Flask, que expone dos rutas:

- `/`: Mensaje de bienvenida simple.
- `/saludo/<nombre>`: Mensaje personalizado.

### 2.3. Definición del Package (Dockerfile)

El paquete (artefacto) se define en el `Dockerfile`. Esta imagen contiene un entorno Python liviano (`python:3.12-slim`), instala las dependencias y ejecuta la aplicación:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80
CMD ["python", "app.py"]
```

---

## 3. Pruebas Automáticas (Testing)

Para asegurar la calidad del código, se definieron pruebas unitarias simples en el archivo `test_app.py` que verifican que las rutas de la aplicación Flask funcionen como se espera.

### 3.1. Contenido de `test_app.py`

```python
import pytest
from app import app 

def test_home_page():
    """ Verifica que la ruta principal '/' funcione correctamente. """
    app.config['TESTING'] = True 
    client = app.test_client()
    response = client.get('/')
    
    assert response.status_code == 200
    assert b"Hola desde Flask con Traefik" in response.data

def test_saludo_personalizado():
    """ Verifica que la ruta '/saludo/<nombre>' retorne el saludo. """
    app.config['TESTING'] = True 
    client = app.test_client()

    test_name = "Pedro"
    response = client.get(f'/saludo/{test_name}')
    
    assert response.status_code == 200
    expected_text = f"Hola {test_name}, bienvenido daniela cardenas "
    assert expected_text.encode('utf-8') in response.data
```

### 3.2. Ejecución en el Pipeline

El paso **Run tests** del GitHub Actions se encarga de ejecutar todas las pruebas:

```yaml
- name: Run tests
  run: pytest
```

> **Nota:** Si alguna prueba falla, el pipeline de CI se detiene inmediatamente, evitando que se construya y publique una imagen Docker con errores.

---

## 4. Pasos para Reproducir el Ciclo

Para que este pipeline sea totalmente reproducible, se requieren los siguientes pasos:

1.  **Configurar el Repositorio:** Asegúrate de que este proyecto esté en un repositorio público de GitHub con todos los archivos (`app.py`, `Dockerfile`, `requirements.txt`, `test_app.py`, y la carpeta `.github/workflows` con `docker.yml`).

2.  **Activar el Pipeline:** Simplemente realiza un push a la rama `main`:

    ```bash
    git push origin main
    ```

3.  **Observar el Resultado:** Navega a la sección **Actions** de tu repositorio de GitHub. Verás la ejecución del pipeline:
    - Si es exitosa, el log mostrará que las pruebas pasaron (`pytest`) y que la imagen Docker fue construida y publicada en **Packages** (Container Registry) de GitHub.

4.  **Verificar el Package:** La imagen se encontrará en `ghcr.io/dano-19/daniela-deber:latest` (o la ruta correspondiente a tu usuario).

---

## 5. Archivos de Despliegue (CD - Despliegue)

Aunque el pipeline se detiene en la Construcción del Package, se incluyen archivos para el despliegue final en un entorno Docker Swarm/Traefik:

- **`stack.yml` (Docker Compose):** Define el servicio `daniapp` usando la imagen generada y configurando etiquetas para el reverse proxy Traefik, exponiendo la aplicación en el dominio `daniapp.byronrm.com`.
- **`Makefile`:** Contiene atajos para gestionar la imagen (`build`) y el despliegue (`deploy` y `rm`) en un entorno Swarm/Traefik preconfigurado.

```makefile
build:
	@docker build -t danimg:latest .

deploy:
	@docker stack deploy --with-registry-auth -c stack.yml quinto

rm:
	@docker stack rm quinto
```
