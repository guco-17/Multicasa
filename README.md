# Multicasa

Proyecto Django para el sistema inmobiliario Multicasa, desarrollado siguiendo los requisitos de análisis, arquitectura y modelo físico de base de datos incluidos en la documentación del proyecto.

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

## Requisitos cubiertos

- Patrón MTV de Django
- API REST con Django REST Framework
- Base de datos MySQL compatible con el modelo físico de datos
- Módulo público y módulo administrativo
- Estructura de directorios proporcional a la arquitectura del proyecto
- Soporte para formularios de contacto y reportes analíticos
