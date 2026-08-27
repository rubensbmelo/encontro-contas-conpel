import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "conpel_encontro.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas_fiscais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            data TEXT NOT NULL,
            numero_nf TEXT NOT NULL,
            valor REAL NOT NULL,
            link_drive TEXT,
            observacao TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # Check if empty, populate initial Agosto data
    cursor.execute("SELECT COUNT(*) FROM notas_fiscais")
    count = cursor.fetchone()[0]
    if count == 0:
        initial_data = [
            ('AGOSTO', '2026-08-04', '17360', 50122.43, 'https://drive.google.com/file/d/1cflk0IP_m4GqaFc8xvPaMToyMs2_j3Kg/view?usp=drive_link', '1ª remessa do mês'),
            ('AGOSTO', '2026-08-04', '17389', 38226.80, 'https://drive.google.com/file/d/1JlclQDJ9VgVNodW4AaZYGi7rnzPjXUOY/view?usp=drive_link', '2ª remessa do mês'),
            ('AGOSTO', '2026-08-17', '17744', 19068.94, 'https://drive.google.com/file/d/1J2m-bmHPXTGrXBxt14hm9qWJuAbVM-MJ/view?usp=drive_link', 'Materiais especiais'),
            ('AGOSTO', '2026-08-20', '17857', 26703.85, 'https://drive.google.com/file/d/1CoCKEQTstDbJCL4OeadjVKBUL_h7otbM/view?usp=drive_link', 'Faturamento quinzenal'),
            ('AGOSTO', '2026-08-26', '18096', 15876.21, 'https://drive.google.com/file/d/1gvbNxshnhWvIIyQeMjwZFSPXKAU5Gw6i/view?usp=drive_link', 'Fechamento parcial')
        ]
        cursor.executemany("""
            INSERT INTO notas_fiscais (mes, data, numero_nf, valor, link_drive, observacao)
            VALUES (?, ?, ?, ?, ?, ?)
        """, initial_data)
        conn.commit()
    conn.close()

def get_notas_by_mes(mes):
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM notas_fiscais WHERE mes = ? ORDER BY data ASC, id ASC", conn, params=(mes,))
    conn.close()
    return df

def get_all_notas():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM notas_fiscais ORDER BY id ASC", conn)
    conn.close()
    return df

def add_nota(mes, data, numero_nf, valor, link_drive, observacao):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notas_fiscais (mes, data, numero_nf, valor, link_drive, observacao)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (mes, data, numero_nf, valor, link_drive, observacao))
    conn.commit()
    conn.close()

def delete_nota(nota_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notas_fiscais WHERE id = ?", (nota_id,))
    conn.commit()
    conn.close()

def update_nota(nota_id, mes, data, numero_nf, valor, link_drive, observacao):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notas_fiscais 
        SET mes = ?, data = ?, numero_nf = ?, valor = ?, link_drive = ?, observacao = ?
        WHERE id = ?
    """, (mes, data, numero_nf, valor, link_drive, observacao, nota_id))
    conn.commit()
    conn.close()
