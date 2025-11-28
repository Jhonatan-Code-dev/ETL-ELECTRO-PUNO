# ⚡ ETL ElectroPuno

Sistema ETL para procesar datos de consumo eléctrico y cargarlos en SQL Server.

## 📋 Descripción

Este proyecto automatiza la extracción, transformación y carga de datos desde archivos CSV hacia una base de datos SQL Server dimensional, facilitando el análisis de consumo eléctrico por cliente, período y ubicación.

## 🏗️ Estructura del Proyecto

```text
ETL-ELECTRO-PUNO/
├── config/
│   └── env_vars.py
├── db/
│   ├── conexion.py
│   └── sql/
│       └── puno.sql
└── tools/
    ├── msodbcsql.msi
    └── python-3.14.0-amd64.exe
```
## 🗄️ Modelo de Datos

```text
**Dimensiones:**
- Client → Clientes  
- Period → Períodos (año/mes)  
- Location → Ubicaciones (ubigeo, distrito, provincia, departamento)

**Hechos:**
- Fact → Consumo, montos y estados de clientes
```
