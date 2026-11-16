# Multicasa

Plataforma inmobiliaria desarrollada en Django y Python, diseñada a partir del modelado físico relacional y levantamiento de requerimientos del sistema Multicasa. Permite la gestión integral del catálogo de inmuebles, filtrado avanzado, control de estados (disponible, reservado, vendido/rentado) y administración de perfiles de usuario mediante Django ORM.

## Requisitos

- Python 3.13+
- Django 6.1.3
- MySQL 8+ para producción
- Entorno virtual `.venv`

## Configuración rápida

1. Crear y activar el entorno virtual:

```powershell
cd C:\Users\Usuario\Documents\GitHub\Multicasa
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

3. Copiar la configuración de entorno:

```powershell
Copy-Item .env.example .env
```

4. Ajustar los valores de la base de datos en `.env` para MySQL.

5. Ejecutar migraciones:

```powershell
python manage.py migrate
```

6. Crear un superusuario:

```powershell
python manage.py createsuperuser
```

7. Iniciar el proyecto:

```powershell
python manage.py runserver
```

## Configuración recomendada para MySQL

```env
DB_ENGINE=mysql
DB_NAME=multicasa_db
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

## Estructura principal

- `apps/casas`: propiedades, imágenes y API REST de inmuebles
- `apps/contacto`: formulario de contacto y envío de correos
- `apps/reportes`: reportes y dashboard administrativo
- `apps/usuarios`: autenticación y acceso administrativo
- `templates/`: plantillas HTML del sitio
- `static/`: archivos CSS y assets generales
- `media/`: imágenes cargadas por el administrador

## Interfaz y recursos visuales

- La página principal reproduce la composición del diseño de Bienes Raíces Multicasa
  con Bootstrap 5.3.3 y estilos propios en `static/css/styles.css`.
- Los recursos del diseño se encuentran en `static/assets/` y se sirven mediante
  la etiqueta `{% static %}` de Django.
- Bootstrap CSS y JavaScript se cargan desde jsDelivr; para ver el diseño completo,
  el navegador necesita acceso a Internet.

## Requisitos cubiertos

- Patrón MTV de Django
- API REST con Django REST Framework
- Base de datos MySQL compatible con el modelo físico de datos
- Módulo público y módulo administrativo
- Estructura de directorios proporcional a la arquitectura del proyecto
- Soporte para formularios de contacto y reportes analíticos

## Pruebas unitarias

Las pruebas están organizadas en `tests/unit/` por módulo. Para ejecutarlas:

```powershell
python manage.py test tests
```

## Integración continua y protección de `main`

El workflow `.github/workflows/ci.yml` ejecuta las comprobaciones de Django,
verifica que no falten migraciones, aplica migraciones y corre las pruebas con
MySQL 8.4 en cada pull request dirigido a `main`.

Para impedir merges cuando el workflow falla, configura una regla en GitHub:

1. Abre **Settings → Rules → Rulesets** (o **Settings → Branches**).
2. Crea una regla para la rama `main`.
3. Activa **Require a pull request before merging**.
4. Activa **Require status checks to pass** y selecciona
   **Django CI / django-tests**.
5. Guarda la regla y asegúrate de que aplique a `main`.

El workflow ejecuta las pruebas; la regla de rama es la que bloquea el merge.
