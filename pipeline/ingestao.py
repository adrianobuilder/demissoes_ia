"""CSV -> raw.eventos.

Spec: validar arquivo e as 20 colunas antes de abrir o banco. CSV UTF-8 com BOM
opcional, vírgula, campos textuais, keep_default_na=False. Preservar conteúdo e
duplicatas; cabeçalho apenas é entrada vazia válida. Substituir em transação,
rollback em falha e mensagens UTF-8 somente após commit. Reexecutar não acumula.
Executar com: uv run python -m pipeline.ingestao.
"""

import csv

import duckdb
import pandas as pd

from pipeline import db

ARQUIVO = db.ARQUIVO_RAW
COLUNAS = [
    "Company",
    "Date",
    "Sector",
    "Country",
    "Functions",
    "Roles counted",
    "Roles reported (not counted)",
    "Why not counted",
    "% of workforce",
    "Evidence tier",
    "Attribution",
    "Execution",
    "Counts in US index",
    "Claim",
    "Source",
    "Source URL",
    "Event ID",
    "Kind",
    "What the employer said",
    "Job families",
]


def ler_arquivo() -> pd.DataFrame:
    with ARQUIVO.open(encoding="utf-8-sig", newline="") as arquivo:
        cabecalho = next(csv.reader(arquivo), [])
    if len(cabecalho) != len(set(cabecalho)):
        raise ValueError("Cabeçalho tem colunas duplicadas")
    faltantes = sorted(set(COLUNAS) - set(cabecalho))
    extras = sorted(set(cabecalho) - set(COLUNAS))
    if faltantes or extras:
        raise ValueError(f"Cabeçalho inválido; faltantes={faltantes}; extras={extras}")
    return pd.read_csv(ARQUIVO, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def executar() -> int:
    dados = ler_arquivo()
    con = db.conectar()
    try:
        con.execute("BEGIN")
        try:
            db.criar_schema(con, "raw")
            linhas = db.gravar(con, "raw", "eventos", dados)
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
    finally:
        con.close()
    return linhas


def main():
    db.configurar_stdout()
    try:
        linhas = executar()
    except (OSError, ValueError, duckdb.Error, pd.errors.ParserError) as exc:
        raise SystemExit(f"Erro na ingestão: {exc}") from exc
    print(f"✓ raw.eventos: {linhas:,} linhas".replace(",", "."))


if __name__ == "__main__":
    main()
