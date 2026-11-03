"""Materializar cada SELECT numerado em uma tabela do schema marts.

Spec: validar nomes NN_nome.sql e colisões antes da conexão; exigir as duas
tabelas refined. Aceitar um SELECT (também com comentários/CTEs), sem modificar
sua regra. Recriar schema inteiro em uma transação, removendo marts obsoletos.
Pasta vazia, dependência ausente, SQL inválido ou resultado vazio preservam o
conjunto anterior. Mensagens e totais UTF-8 só depois do commit.
"""

import re

import duckdb

from pipeline import db

PASTA_SQL = db.PASTA_SQL


def descobrir():
    arquivos = sorted(
        (p for p in PASTA_SQL.iterdir() if p.is_file() and p.suffix.lower() == ".sql"),
        key=lambda p: p.name,
    )
    if not arquivos:
        raise ValueError("Nenhum SQL encontrado em sql/marts")
    nomes = set()
    consultas = []
    for arquivo in arquivos:
        if not re.fullmatch(r"[0-9]{2}_[a-z][a-z0-9_]*\.sql", arquivo.name, re.IGNORECASE):
            raise ValueError(f"Nome inválido: {arquivo.name}; esperado NN_nome.sql")
        nome = arquivo.stem[3:].lower()
        if nome in nomes:
            raise ValueError(f"Nome de mart duplicado: {nome}")
        nomes.add(nome)
        consultas.append((arquivo, nome))
    return consultas


def executar():
    consultas = descobrir()
    if not db.BANCO.is_file():
        raise FileNotFoundError(f"Banco ausente: {db.BANCO}; execute pipeline.transformacao")
    con = db.conectar()
    resultados = []
    try:
        existentes = {
            r[0]
            for r in con.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'refined'"
            ).fetchall()
        }
        faltantes = sorted({"eventos", "evento_familia"} - existentes)
        if faltantes:
            raise ValueError(
                f"Tabelas refined ausentes: {faltantes}; execute pipeline.transformacao"
            )
        con.execute("BEGIN")
        try:
            con.execute("DROP SCHEMA IF EXISTS marts CASCADE")
            db.criar_schema(con, "marts")
            for arquivo, nome in consultas:
                try:
                    sql = arquivo.read_text(encoding="utf-8").strip().removesuffix(";")
                    comandos = con.extract_statements(sql)
                    if len(comandos) != 1 or comandos[0].type != duckdb.StatementType.SELECT:
                        raise ValueError("Esperado um único SELECT, com WITH opcional")
                    con.execute(f"CREATE TABLE marts.{db.identificador(nome)} AS {sql}")
                    linhas = con.execute(
                        f"SELECT count(*) FROM marts.{db.identificador(nome)}"
                    ).fetchall()[0][0]
                    if not linhas:
                        raise ValueError("Mart vazio; carga anterior preservada")
                    resultados.append((nome, linhas))
                except (OSError, ValueError, duckdb.Error) as exc:
                    raise ValueError(f"{arquivo.name}: {exc}") from exc
            con.execute("COMMIT")
        except OSError, ValueError, duckdb.Error:
            con.execute("ROLLBACK")
            raise
    finally:
        con.close()
    return resultados


def main():
    db.configurar_stdout()
    try:
        resultados = executar()
    except (OSError, ValueError, duckdb.Error) as exc:
        raise SystemExit(f"Erro nos marts: {exc}") from exc
    for nome, linhas in resultados:
        print(f"✓ marts.{nome}: {linhas:,} linhas".replace(",", "."))
    total = f"{sum(n for _, n in resultados):,}".replace(",", ".")
    print(f"Total: {len(resultados)} marts, {total} linhas")


if __name__ == "__main__":
    main()
