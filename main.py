import time
from datetime import datetime
from join_data.merge_files import ejecutar_union
from etl.etl_load import run_etl

# RUTA_MANUAL = r"C:\Users\Desktop\union_all.csv"
RUTA_MANUAL = None

def log_tiempo(nombre_proceso, inicio):
    fin = time.time()
    duracion = fin - inicio
    print(f"{nombre_proceso} completado en {duracion:.2f} segundos\n")
    return duracion

if __name__ == "__main__":
    print("==============================================")
    print("INICIO DEL PROCESO ETL")
    print("Inicio:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("==============================================\n")

    tiempo_total_inicio = time.time()

    if RUTA_MANUAL:
        print("Modo manual activado.")
        print(f"Archivo: {RUTA_MANUAL}\n")

        inicio_etl = time.time()
        run_etl(RUTA_MANUAL)
        log_tiempo("ETL", inicio_etl)

    else:
        print("Modo automático activado.\n")
        inicio_union = time.time()
        ruta_final = ejecutar_union()
        log_tiempo("Unión de archivos", inicio_union)
        print(f"Archivo generado: {ruta_final}\n")
        if ruta_final:
            inicio_etl = time.time()
            run_etl(ruta_final)
            log_tiempo("ETL", inicio_etl)
        else:
            print("No se generó archivo final. Proceso detenido.\n")

    tiempo_total = time.time() - tiempo_total_inicio

    print("==============================================")
    print(f"PROCESO COMPLETO EN {tiempo_total:.2f} segundos")
    print("Fin:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("==============================================")
