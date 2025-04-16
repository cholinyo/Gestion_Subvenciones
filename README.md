# 🏛️ Gestión de Subvenciones

Aplicación web desarrollada con **Flask** y **SQLite** para gestionar el ciclo de vida de las solicitudes de subvención. Permite registrar, editar, hacer seguimiento y controlar documentación y observaciones de cada solicitud.

## 🚀 Características principales

- Gestión completa del ciclo de vida de una solicitud de subvención.
- Estados definidos del proceso: `en tramitación`, `solicitada`, `concedida`, `denegada`, etc.
- Historial de cambios y observaciones.
- Control de documentación requerida.
- Campos obligatorios según estado.
- Control de acceso por roles (`ADMIN`, `GESTOR`, `CONSULTA`).
- Interfaz web intuitiva, responsive y optimizada para el trabajo diario del personal técnico.

## 🛠️ Tecnologías utilizadas

- Python 3.12
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Migrate
- Bootstrap 5
- SQLite (entorno desarrollo)

## 🧱 Estructura del proyecto

```
Gestion_Subvenciones/
│
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── solicitud_subvencion.py
│   │   ├── observacion_solicitud.py
│   │   └── ...
│   ├── routes/
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── solicitudes.py
│   ├── templates/
│   │   └── solicitudes/
│   │       ├── lista.html
│   │       ├── editar.html
│   │       └── nueva.html
│   └── utils/
│       └── validate_solicitud_estado.py
│
├── migrations/
│
├── config.py
├── run.py
└── README.md
```

## ⚙️ Configuración y ejecución

### 1. Clonar repositorio

```bash
git clone https://github.com/cholinyo/Gestion_Subvenciones.git
cd Gestion_Subvenciones
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/Scripts/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Iniciar base de datos

Si es la primera vez:

```bash
flask db init
flask db migrate -m "Inicial"
flask db upgrade
```

### 4. Ejecutar aplicación

```bash
flask run
```

Abre tu navegador en `http://127.0.0.1:5000`.

## 🧪 Pruebas funcionales

- Crear una nueva solicitud.
- Editar y cambiar su estado paso a paso.
- Validar campos obligatorios por estado.
- Añadir observaciones.
- Visualizar y filtrar por estado en el listado.

## 👤 Autor

Desarrollado por **Vicente Caruncho**.

## 📝 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**.
