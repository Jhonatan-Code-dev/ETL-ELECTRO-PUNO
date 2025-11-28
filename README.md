# Flujo Completo de Extracción, Transformación y Carga (ETL) para Datos de Consumo Eléctrico

Este proyecto implementa un sistema automatizado de Extracción, Transformación y Carga (ETL) diseñado para el procesamiento masivo y consolidación de registros de consumo eléctrico. El sistema permite la integración eficiente de archivos de datos en formato CSV hacia una base de datos relacional SQL Server, garantizando la integridad y disponibilidad de la información para su posterior análisis.

## Fuente de Datos

El sistema procesa información proveniente de datos abiertos oficiales proporcionados por el Estado Peruano.

- **Nombre del Conjunto de Datos**: [Consumo de Energía Eléctrica de los clientes de Electro Puno S.A.A.](https://www.datosabiertos.gob.pe/dataset/consumo-de-energ%C3%ADa-el%C3%A9ctrica-de-los-clientes-de-electro-puno-saa)
- **Entidad Publicadora**: Electro Puno S.A.A.
- **Frecuencia de Actualización**: Mensual
- **Descripción del Contenido**:
  > Este conjunto de datos contiene el registro mensual del consumo de energía eléctrica de los usuarios en la región de Puno. Cada registro representa un suministro eléctrico caracterizado por: código de UBIGEO, fecha de alta, tarifa vigente, periodo de consumo, consumo en Kwh, estado del cliente y ubicación geográfica (departamento, provincia y distrito). La identidad del titular del suministro se encuentra anonimizada para proteger la privacidad.

## Arquitectura del Proyecto

La estructura del código fuente se organiza de la siguiente manera:

```text
├── etl/                # Módulos principales del proceso ETL
│   ├── extract.py      # Lógica de extracción de datos
│   ├── transform.py    # Lógica de limpieza y transformación
│   ├── load.py         # Lógica de carga a SQL Server
│   └── etl_load.py     # Orquestador del flujo de trabajo
├── join_data/          # Módulos para la unificación de archivos
│   └── merge_files.py  # Script de fusión de archivos CSV
├── db/                 # Contiene el script SQL de creación de la base de datos
├── config/             # Archivos de configuración global
├── logs/               # Directorio de registros de ejecución
├── main.py             # Punto de entrada principal de la aplicación
├── tools/              # Contiene instaladores de herramientas necesarias
├── .env                # Variables de entorno y credenciales
```

## Requisitos del Sistema

Para la correcta ejecución del software, se requiere:

- **Lenguaje de Programación**: Python 3.8 o superior.
- **Sistema de Gestión de Base de Datos**: SQL Server (Instancia local o remota).
- **Controlador de Base de Datos**: ODBC Driver 17 for SQL Server (o versión compatible).

## Esquema de Base de Datos

El sistema requiere una estructura de base de datos específica. A continuación se presenta el script SQL para la creación de las tablas necesarias:

```sql
CREATE DATABASE [ElectroPuno];
GO

USE [ElectroPuno];
GO

CREATE TABLE [dbo].[Client] (
    [client_id] INT PRIMARY KEY
);
GO

CREATE TABLE [dbo].[Period] (
    [period_id] INT IDENTITY(1,1) PRIMARY KEY,
    [year] SMALLINT NOT NULL,
    [month] TINYINT NOT NULL,
);
GO

CREATE TABLE [dbo].[Location] (
    [location_id] INT IDENTITY(1,1) PRIMARY KEY,
    [ubigeo] CHAR(6) NOT NULL,
    [district] VARCHAR(200) NOT NULL,
    [province] VARCHAR(200) NOT NULL,
    [department] VARCHAR(200) NOT NULL
);
GO

CREATE TABLE [dbo].[Fact] (
    [client_id] INT NOT NULL,
    [period_id] INT NOT NULL,
    [location_id] INT NOT NULL,
    [amount] DECIMAL(9,2) NULL,
    [consumption] DECIMAL(9,2) NULL,
    [client_state] CHAR(2) NULL,
    CONSTRAINT [FK_Fact_Client] FOREIGN KEY ([client_id]) REFERENCES [dbo].[Client] ([client_id]),
    CONSTRAINT [FK_Fact_Period] FOREIGN KEY ([period_id]) REFERENCES [dbo].[Period] ([period_id]),
    CONSTRAINT [FK_Fact_Location] FOREIGN KEY ([location_id]) REFERENCES [dbo].[Location] ([location_id])
);
GO
```

## Instalación y Despliegue

Siga los siguientes pasos para desplegar el entorno de desarrollo:

1.  **Obtención del Código Fuente**:
    Descargue o clone el repositorio en el directorio de trabajo deseado.

2.  **Instalación de Dependencias**:
    Ejecute los siguientes comandos para instalar las bibliotecas necesarias:
    ```bash
    pip install pyodbc==5.3.0
    pip install python-dotenv==1.2.1
    pip install chardet==5.2.0
    pip install pandas==2.3.3
    ```

## Configuración

El sistema utiliza variables de entorno para la configuración de parámetros sensibles y rutas de ejecución. Debe crear un archivo `.env` en el directorio raíz con las siguientes definiciones:

| Variable          | Descripción                                    | Ejemplo                      |
| :---------------- | :--------------------------------------------- | :--------------------------- |
| `SQL_SERVER`      | Dirección IP o nombre de host del servidor SQL | `LAPTOP-KNVOVQ9L\SQLEXPRESS` |
| `SQL_DATABASE`    | Nombre de la base de datos de destino          | `ElectroPuno`                |
| `CARPETA_CSV`     | Ruta absoluta del directorio de archivos CSV   | `C:\Datos\Entrada`           |
| `ETL_OUTPUT_FILE` | Nombre del archivo temporal consolidado        | `UNION_ALL.csv`              |

**Ejemplo de configuración (`.env`):**

```ini
SQL_SERVER=LAPTOP-KNVOVQ9L\SQLEXPRESS
SQL_DATABASE=ElectroPuno
CARPETA_CSV=C:\Users\Admin\Desktop\DATA
ETL_OUTPUT_FILE=UNION_ALL.csv
```

## Manual de Operación

El sistema ofrece dos modalidades de operación según los requerimientos del usuario:

### 1. Modo Automático (Predeterminado)

Este modo está diseñado para el procesamiento por lotes. El sistema escaneará el directorio definido en `CARPETA_CSV`, unificará todos los archivos encontrados y procederá con la carga a la base de datos.

**Procedimiento:**

1.  Verifique que la variable `RUTA_MANUAL` en el archivo `main.py` esté configurada como `None`.
2.  Ejecute el script principal:
    ```bash
    python main.py
    ```

### 2. Modo Manual

Este modo permite el procesamiento de un único archivo específico, ideal para pruebas unitarias o reprocesamiento de datos.

**Procedimiento:**

1.  Edite el archivo `main.py`.
2.  Asigne a la variable `RUTA_MANUAL` la ruta absoluta del archivo a procesar:
    ```python
    RUTA_MANUAL = r"C:\Ruta\Al\Archivo\Especifico.csv"
    ```
3.  Ejecute el script principal:
    ```bash
    python main.py
    ```

## Monitoreo y Logs

Durante la ejecución, el sistema emitirá información detallada en la consola estándar, permitiendo el seguimiento del progreso y el rendimiento de cada etapa:
