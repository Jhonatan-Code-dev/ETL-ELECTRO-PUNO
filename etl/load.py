def insert_clients(cursor, conn, client_ids):
    cursor.fast_executemany = True
    cursor.executemany(
        """
        IF NOT EXISTS (SELECT 1 FROM Client WHERE client_id = ?)
        INSERT INTO Client (client_id) VALUES (?);
        """,
        [(cid, cid) for cid in client_ids]
    )
    conn.commit()


def insert_periods(cursor, conn, periods):
    cursor.executemany(
        """
        IF NOT EXISTS (SELECT 1 FROM Period WHERE year = ? AND month = ?)
        INSERT INTO Period (year, month) VALUES (?, ?);
        """,
        [(y, m, y, m) for y, m in periods]
    )
    conn.commit()


def insert_locations(cursor, conn, locations):
    cursor.fast_executemany = True
    cursor.executemany(
        """
        IF NOT EXISTS (SELECT 1 FROM Location WHERE ubigeo = ?)
        INSERT INTO Location (ubigeo, district, province, department)
        VALUES (?, ?, ?, ?);
        """,
        [
            (
                row["UBIGEO_NORM"],
                row["UBIGEO_NORM"],
                row["DISTRITO"],
                row["PROVINCIA"],
                row["DEPARTAMENTO"]
            )
            for _, row in locations.iterrows()
        ]
    )
    conn.commit()


def insert_fact_batch(cursor, batch):
    cursor.fast_executemany = True
    cursor.executemany(
        """
        INSERT INTO Fact (client_id, period_id, location_id, amount, consumption, client_state)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        batch
    )
