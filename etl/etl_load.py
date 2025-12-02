import os
from db.conexion import get_sql_connection
from .settings import ERROR_LOG, COLUMNS, BATCH_SIZE
from etl.extract import load_csv
from etl.transform import clean_text, format_period, normalize_ubigeo, transform_client_state
from etl.load_helpers import (insert_clients,insert_periods,insert_locations,insert_fact_batch)

def run_etl(ruta_final):
    if os.path.exists(ERROR_LOG):
        os.remove(ERROR_LOG)
    df = load_csv(ruta_final)[COLUMNS]
    df["DEPARTAMENTO"] = df["DEPARTAMENTO"].map(clean_text)
    df["PROVINCIA"] = df["PROVINCIA"].map(clean_text)
    df["DISTRITO"] = df["DISTRITO"].map(clean_text)

    df["UBIGEO_NORM"] = df["UBIGEO"].map(normalize_ubigeo)
    df["YEAR"], df["MONTH"] = zip(*df["PERIODO"].map(format_period))
    df["ESTADO_NORM"] = df["ESTADO_CLIENTE"].map(transform_client_state)

    conn = get_sql_connection()
    cursor = conn.cursor()

    insert_clients(cursor, conn,
        df["CÓDIGO_CLIENTE"].astype(int).drop_duplicates().tolist()
    )

    insert_periods(cursor, conn,
        df[["YEAR", "MONTH"]].drop_duplicates().values.tolist()
    )

    insert_locations(cursor, conn,
        df[["UBIGEO_NORM", "DISTRITO", "PROVINCIA", "DEPARTAMENTO"]].drop_duplicates()
    )

    cursor.execute("SELECT client_id FROM Client;")
    client_map = {cid: cid for cid, in cursor.fetchall()}

    cursor.execute("SELECT period_id, year, month FROM Period;")
    period_map = {(y, m): pid for pid, y, m in cursor.fetchall()}

    cursor.execute("SELECT location_id, ubigeo FROM Location;")
    location_map = {ub: lid for lid, ub in cursor.fetchall()}

    df["client_id"] = df["CÓDIGO_CLIENTE"].astype(int).map(client_map)

    df["period_id"] = df[["YEAR", "MONTH"]].apply(tuple, axis=1).map(period_map)
    df["location_id"] = df["UBIGEO_NORM"].map(location_map)
    df_fact = df[[
        "client_id", "period_id", "location_id",
        "FACTURACIÓN", "CONSUMO", "ESTADO_NORM"
    ]].drop_duplicates(
        subset=["client_id", "period_id", "location_id"], 
        keep='first'
    )

    df_fact["FACTURACIÓN"] = df_fact["FACTURACIÓN"].astype(float)
    df_fact["CONSUMO"] = df_fact["CONSUMO"].astype(float)
    cursor.execute("SELECT client_id, period_id, location_id FROM Fact;")
    existentes = set(tuple(row) for row in cursor.fetchall())

    df_fact["key"] = df_fact.apply(
        lambda x: (x.client_id, x.period_id, x.location_id), axis=1
    )
    df_fact = df_fact[~df_fact["key"].isin(existentes)]
    df_fact = df_fact.drop(columns=["key"])
    duplicados_finales = df_fact.duplicated(
        subset=["client_id", "period_id", "location_id"]
    ).sum()
    
    if duplicados_finales > 0:
        print(f"ADVERTENCIA: Se encontraron {duplicados_finales} duplicados después de la limpieza")
        df_fact = df_fact.drop_duplicates(
            subset=["client_id", "period_id", "location_id"], 
            keep='first'
        )

    total = len(df_fact)

    for i in range(0, total, BATCH_SIZE):
        batch = df_fact.iloc[i:i+BATCH_SIZE].values.tolist()
        insert_fact_batch(cursor, batch)
        conn.commit()

    cursor.close()
    conn.close()

    print(f"ETL completado. Nuevos insertados: {total}")