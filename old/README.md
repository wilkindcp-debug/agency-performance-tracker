# Agency Performance Tracker 🏦

Plataforma web interna para el seguimiento mensual del desempeño de jefes de agencia.

## Características

- ✅ Registro de agencias y jefes
- ✅ Definición de KPIs por agencia (CS, RIA, MG, CORNERS)
- ✅ Objetivos 2026 distribuidos por mes
- ✅ Registro de resultados reales mensuales
- ✅ Notas de seguimiento ("Qué pasó" y "Plan de mejora")
- ✅ Checklist de acciones por mes
- ✅ Dashboard con semáforos y ranking
- ✅ Histórico completo consultable

## Tecnologías

- **Python** 3.11+
- **Streamlit** - Frontend/UI
- **SQLAlchemy** - ORM
- **SQLite** (desarrollo) / **PostgreSQL** (producción)

## Instalación

### 1. Clonar/copiar el proyecto

```bash
cd agency-performance-tracker
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# o en Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -U pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env si necesita cambiar la base de datos
```

### 5. Inicializar base de datos

```bash
python -m db.init_db
```

### 6. Cargar KPIs iniciales

```bash
python -m scripts.init_kpis
```

### 7. Ejecutar la aplicación

```bash
streamlit run main.py
```

La aplicación estará disponible en `http://localhost:8501`

## Estructura del Proyecto

```
agency-performance-tracker/
├── main.py                 # Entrada principal
├── requirements.txt        # Dependencias
├── .env.example           # Variables de entorno ejemplo
├── README.md
│
├── db/
│   ├── __init__.py
│   ├── database.py        # Configuración SQLAlchemy
│   ├── models.py          # Modelos ORM
│   └── init_db.py         # Script inicialización DB
│
├── services/
│   ├── __init__.py
│   ├── agency_service.py  # Lógica de agencias
│   ├── kpi_service.py     # Lógica de KPIs
│   ├── tracking_service.py # Objetivos/resultados/notas
│   └── utils.py           # Utilidades
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py         # Navegación
│   ├── agency_setup.py    # Crear agencia
│   ├── agency_list.py     # Listar agencias
│   ├── targets_setup.py   # Objetivos mensuales
│   ├── monthly_review.py  # Seguimiento mensual
│   └── dashboard.py       # Dashboard general
│
├── scripts/
│   ├── __init__.py
│   └── init_kpis.py       # Seed de KPIs
│
└── data/
    └── exports/           # Backups/exports
```

## Uso

### Crear una Agencia

1. Ir a "Crear Agencia" en el menú lateral
2. Completar datos de la agencia y del jefe
3. Seleccionar los KPIs a medir
4. Guardar

### Definir Objetivos

1. Ir a "Objetivos 2026"
2. Seleccionar agencia y mes
3. Ingresar valores objetivo para cada KPI
4. Usar "Copiar a todos los meses" para replicar

### Seguimiento Mensual

1. Ir a "Seguimiento Mensual"
2. Seleccionar agencia, año y mes
3. Pestaña "Resultados": ingresar valores reales
4. Pestaña "Notas": documentar qué pasó y plan de mejora
5. Pestaña "Acciones": crear checklist de tareas

### Dashboard

- Vista general de todas las agencias
- Ranking por cumplimiento
- Alertas de agencias con KPIs en rojo

## KPIs Predefinidos

| Código | Descripción | Unidad |
|--------|-------------|--------|
| Capital Services | Capital Services | trx |
| RIA | Remesas Internacionales | units |
| MG | MoneyGram | units |
| CORNERS | Puntos de Venta | units |

## Semáforos

- 🟢 **Verde**: >= 100% del objetivo
- 🟡 **Amarillo**: 90-99% del objetivo
- 🔴 **Rojo**: < 90% del objetivo

## Producción (PostgreSQL)

Para usar PostgreSQL en producción, edite `.env`:

```
DATABASE_URL=postgresql+psycopg2://usuario:password@host:5432/nombre_db
```

Y descomente `psycopg2-binary` en `requirements.txt`.

## Soporte

Para reportar problemas o sugerencias, contacte al equipo de desarrollo.

---
© 2026 - Agency Performance Tracker
