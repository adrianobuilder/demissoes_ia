"""Infraestrutura compartilhada do DuckDB.

Spec: resolver caminhos pela localização deste pacote, nunca pelo cwd; gravar por
substituição, delimitando identificadores SQL e liberando o registro temporário
inclusive em erro. A etapa chamadora controla transações e fecha a conexão.
Leitura read-only exige arquivo existente. Nenhuma função abre o banco Olist.
"""

import sys
from pathlib import Path

import duckdb
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BANCO = RAIZ / "demissao_ia.duckdb"
ARQUIVO_RAW = RAIZ / "raw" / "ai-layoffs-register.csv"
PASTA_SQL = RAIZ / "sql" / "marts"


def configurar_stdout():
    """Streams de teste podem não oferecer reconfigure."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def identificador(nome: str) -> str:
    if not nome or "\x00" in nome:
        raise ValueError("Identificador vazio ou com caractere nulo")
    return '"' + nome.replace('"', '""') + '"'


def conectar(*, read_only=False):
    if read_only and not BANCO.is_file():
        raise FileNotFoundError(f"Banco ausente: {BANCO}")
    return duckdb.connect(str(BANCO), read_only=read_only)


def criar_schema(con, schema: str):
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {identificador(schema)}")


def gravar(con, schema: str, tabela: str, dados: pd.DataFrame) -> int:
    destino = f"{identificador(schema)}.{identificador(tabela)}"
    con.register("_entrada_dataframe", dados)
    try:
        con.execute(f"CREATE OR REPLACE TABLE {destino} AS SELECT * FROM _entrada_dataframe")
        return con.execute(f"SELECT count(*) FROM {destino}").fetchall()[0][0]
    finally:
        con.unregister("_entrada_dataframe")
