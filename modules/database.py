# modules/database.py
# Conexão, inicialização e operações com o banco de dados SQLite.

import sqlite3

import pandas as pd

from modules.seed_data import gera_dataset

DB_PATH = "laudos.db"


def cria_conexao(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Cria e retorna conexão com o banco SQLite."""
    return sqlite3.connect(db_path, check_same_thread=False)


def init_db(conn: sqlite3.Connection) -> None:
    """Cria tabelas e popula com dados sintéticos se o banco estiver vazio."""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_laudos_treino (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_exame TEXT NOT NULL,
            descricao  TEXT NOT NULL,
            criado_em  TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_historico (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_arquivo    TEXT,
            tipo_previsto   TEXT,
            confianca       REAL,
            status          TEXT,
            achados         TEXT,
            conduta         TEXT,
            texto_extraido  TEXT,
            analisado_em    TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM tb_laudos_treino")
    if cursor.fetchone()[0] == 0:
        _popula_treino(conn, cursor)


def _popula_treino(conn: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
    dataset = gera_dataset(n_por_classe=90)
    rows = [(d["tipo_exame"], d["descricao"]) for d in dataset]
    cursor.executemany(
        "INSERT INTO tb_laudos_treino (tipo_exame, descricao) VALUES (?, ?)", rows
    )
    conn.commit()


def carrega_dados_treino(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("SELECT tipo_exame, descricao FROM tb_laudos_treino", conn)


def salva_historico(
    conn: sqlite3.Connection,
    nome_arquivo: str,
    tipo_previsto: str,
    confianca: float,
    status: str,
    achados: str,
    conduta: str,
    texto_extraido: str,
) -> None:
    conn.execute(
        """INSERT INTO tb_historico
           (nome_arquivo, tipo_previsto, confianca, status, achados, conduta, texto_extraido)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (nome_arquivo, tipo_previsto, confianca, status, achados, conduta, texto_extraido),
    )
    conn.commit()


def carrega_historico(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(
        """SELECT id, nome_arquivo, tipo_previsto,
                  ROUND(confianca*100,1) as confianca_pct,
                  status, analisado_em
           FROM tb_historico ORDER BY id DESC""",
        conn,
    )


def busca_detalhe(conn: sqlite3.Connection, laudo_id: int) -> dict | None:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_historico WHERE id = ?", (laudo_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return dict(zip([d[0] for d in cursor.description], row))


def estatisticas(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT tipo_previsto, COUNT(*) as total FROM tb_historico GROUP BY tipo_previsto ORDER BY total DESC",
        conn,
    )
