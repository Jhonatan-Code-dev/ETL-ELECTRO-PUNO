import os
import csv
import pandas as pd
import chardet
from config.env_vars import CARPETA_CSV, ETL_OUTPUT_FILE

ENCABEZADO_OFICIAL = [
    "CÓDIGO_CLIENTE", "UBIGEO", "DEPARTAMENTO", "PROVINCIA", "DISTRITO",
    "FECHA_ALTA", "TARIFA", "PERIODO", "CONSUMO", "FACTURACIÓN",
    "ESTADO_CLIENTE", "FECHA_CORTE"
]

ENCABEZADOS_DETECTABLES = [
    "Codigo", "CodigoUbigeo", "NombreDepartamento", "NombreProvincia",
    "NombreDistrito", "InicioContrato", "Tarifa", "CodigoPeriodoComercial",
    "CEA", "M_Total", "NombreEstadoSuministro", "Fecha"
]

def eliminar_archivo_existente(carpeta, nombre_archivo):
    ruta = os.path.join(carpeta, nombre_archivo)
    if os.path.exists(ruta):
        os.remove(ruta)
        print(f"Archivo previo eliminado: {ruta}")

def detectar_codificacion(path):
    with open(path, "rb") as f:
        datos = f.read(40000)
    return chardet.detect(datos)["encoding"] or "latin1"

def detectar_delimitador(linea):
    delimitadores = [",", ";", "|", "\t"]
    conteos = {d: linea.count(d) for d in delimitadores}
    return max(conteos, key=conteos.get)

def leer_csv_bruto(path, encoding):
    with open(path, "r", encoding=encoding, errors="ignore") as f:
        lineas = [l.rstrip("\n") for l in f.readlines() if l.strip()]
    if not lineas:
        return pd.DataFrame()
    separador = detectar_delimitador(lineas[0])
    filas = [l.split(separador) for l in lineas]
    ancho = max(len(f) for f in filas)
    filas = [f + [""] * (ancho - len(f)) for f in filas]
    return pd.DataFrame(filas)

def detectar_encabezado(df):
    primera = df.iloc[0].tolist()
    coincidencias = sum(1 for col in primera if col in ENCABEZADOS_DETECTABLES)
    return coincidencias >= 3

def procesar_archivo_csv(path):
    print(f"\nProcesando CSV: {os.path.basename(path)}")
    df = leer_csv_bruto(path, detectar_codificacion(path))
    if df.empty:
        print("Archivo vacío o ilegible.")
        return None
    if df.shape[1] > 12:
        df = df.iloc[:, :12]
    elif df.shape[1] < 12:
        print(f"ERROR: El archivo tiene menos de 12 columnas ({df.shape[1]}).")
        return None
    if detectar_encabezado(df):
        df = df.iloc[1:]
    else:
        primera = df.iloc[0].tolist()
        if all(not str(x).isdigit() for x in primera):
            df = df.iloc[1:]
    df.columns = ENCABEZADO_OFICIAL
    print(f"Filas procesadas: {len(df)}")
    return df

def procesar_archivo_excel(path):
    print(f"\nProcesando EXCEL: {os.path.basename(path)}")
    try:
        df = pd.read_excel(path, header=None, dtype=str)
    except Exception as e:
        print(f"ERROR al leer Excel: {e}")
        return None
    if df.empty:
        print("Excel vacío.")
        return None
    df = df.dropna(how='all').reset_index(drop=True)
    fila_1 = df.iloc[0].astype(str).tolist()
    fila_2 = df.iloc[1].astype(str).tolist() if len(df) > 1 else []
    def contar_coincidencias(fila):
        return sum(1 for c in fila if c.replace("\n","").strip() in ENCABEZADOS_DETECTABLES)
    encabezado = fila_2 if contar_coincidencias(fila_2) > contar_coincidencias(fila_1) else fila_1
    df = df.iloc[1:]
    if len(encabezado) > 12:
        encabezado = encabezado[:12]
        df = df.iloc[:, :12]
    elif len(encabezado) < 12:
        print(f"ERROR: Excel tiene menos de 12 columnas ({len(encabezado)}).")
        return None
    df.columns = ENCABEZADO_OFICIAL
    print(f"Filas procesadas: {len(df)}")
    return df

def unir_archivos(carpeta):
    datos_acumulados = []
    total_original = 0
    for archivo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, archivo)
        if archivo.lower().endswith(".csv"):
            df = procesar_archivo_csv(ruta)
        elif archivo.lower().endswith((".xlsx", ".xls")):
            df = procesar_archivo_excel(ruta)
        else:
            continue
        if df is not None and not df.empty:
            datos_acumulados.append(df)
            total_original += len(df)
    if not datos_acumulados:
        print("\nNo se generaron datos finales.")
        return None
    df_union = pd.concat(datos_acumulados, ignore_index=True)
    print("\n--------------------------------------")
    print(f"TOTAL FINAL DE FILAS UNIDAS: {len(df_union)}")
    print(f"TOTAL SUMA DE FILAS ORIGINALES: {total_original}")
    print("VERIFICACIÓN:", "Ninguna línea se perdió." if len(df_union)==total_original else "Falta información.")
    print("--------------------------------------\n")
    return df_union

def exportar_csv(df, carpeta, nombre_archivo):
    salida_csv = os.path.join(carpeta, nombre_archivo)
    print("\nGenerando archivo CSV sin comillas...")
    df.to_csv(
        salida_csv,
        index=False,
        encoding="utf-8-sig",
        sep=";",
        quoting=csv.QUOTE_NONE,
        escapechar="\\"
    )
    print("\nCSV GENERADO CORRECTAMENTE:")
    print(salida_csv)
    return salida_csv

def ejecutar_union():
    eliminar_archivo_existente(CARPETA_CSV, ETL_OUTPUT_FILE)
    df_final = unir_archivos(CARPETA_CSV)
    if df_final is not None:
        ruta_csv = exportar_csv(df_final, CARPETA_CSV, ETL_OUTPUT_FILE)
        return ruta_csv
    return None