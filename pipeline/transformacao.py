"""raw.eventos -> refined.eventos + refined.evento_familia.

Spec: mapa completo das 20 colunas, datas ISO estritas, quantidades BIGINT não
negativas e yes/no obrigatório. Vazios viram NULL; outros textos são preservados.
Remover só duplicata integral após conversão; ID conflitante encerra com amostra.
Expandir famílias por '; ', sem pares repetidos nem órfãos e sem copiar postos.
Uma transação protege as duas tabelas. Raw não muda. Entrada vazia é válida.
Executar com: uv run python -m pipeline.transformacao.
"""

import duckdb

from pipeline import db

COLUNAS = [
    ("Company", "empresa", None),
    ("Date", "data_evento", "DATE"),
    ("Sector", "setor_informado", None),
    ("Country", "pais_informado", None),
    ("Functions", "funcoes_informadas", None),
    ("Roles counted", "postos_contabilizados", "BIGINT"),
    ("Roles reported (not counted)", "postos_reportados_nao_contabilizados", "BIGINT"),
    ("Why not counted", "motivo_nao_contabilizado", None),
    ("% of workforce", "percentual_quadro_texto", None),
    ("Evidence tier", "nivel_evidencia", None),
    ("Attribution", "atribuicao_ia", None),
    ("Execution", "situacao_execucao", None),
    ("Counts in US index", "conta_indice_eua", "BOOLEAN"),
    ("Claim", "descricao_evento", None),
    ("Source", "fonte", None),
    ("Source URL", "fonte_url", None),
    ("Event ID", "evento_id", None),
    ("Kind", "tipo_evento", None),
    ("What the employer said", "posicao_empregador", None),
    ("Job families", "familias_ocupacionais", None),
]
TABELAS = [("eventos", "eventos", COLUNAS, ["evento_id"])]
DOMINIOS = {
    "tipo_evento": ("cut", "workforce statement"),
    "atribuicao_ia": ("explicit", "mixed", "blamed"),
    "situacao_execucao": ("announced", "executed", "partial", "reversed", "unknown"),
    "nivel_evidencia": ("Tier 1", "Tier 2", "Tier 3"),
}


def _expressoes(con):
    expressoes = []
    for origem, destino, tipo in COLUNAS:
        coluna = db.identificador(origem)
        limpa = f"NULLIF(trim({coluna}), '')"
        padrao = "[0-9]+" if tipo == "BIGINT" else "[0-9]{4}-[0-9]{2}-[0-9]{2}"
        if tipo in ("BIGINT", "DATE"):
            invalidos = con.execute(
                f'SELECT "Event ID", {coluna} FROM raw.eventos '
                f"WHERE {limpa} IS NOT NULL AND NOT regexp_full_match({limpa}, ?) LIMIT 5",
                [padrao],
            ).fetchall()
            if invalidos:
                raise ValueError(f"Valor inválido em {origem}: {invalidos}")
            valor = f"CAST({limpa} AS {tipo})"
        elif tipo == "BOOLEAN":
            invalidos = con.execute(
                f'SELECT "Event ID", {coluna} FROM raw.eventos '
                f"WHERE {limpa} IS NULL OR {limpa} NOT IN ('yes', 'no') LIMIT 5"
            ).fetchall()
            if invalidos:
                raise ValueError(f"Esperado yes/no em {origem}: {invalidos}")
            valor = f"CASE WHEN {limpa} = 'yes' THEN TRUE ELSE FALSE END"
        else:
            valor = f"CASE WHEN {limpa} IS NULL THEN NULL ELSE {coluna} END"
        expressoes.append(f"{valor} AS {db.identificador(destino)}")
    return expressoes


def _validar_staging(con):
    for coluna in ("evento_id", "empresa", "data_evento", "tipo_evento"):
        total = con.execute(
            f"SELECT count(*) FROM _staging_eventos WHERE {db.identificador(coluna)} IS NULL"
        ).fetchall()[0][0]
        if total:
            raise ValueError(f"Campo obrigatório {coluna}: {total} valores ausentes")
    for coluna, valores in DOMINIOS.items():
        nome = db.identificador(coluna)
        marcadores = ", ".join("?" for _ in valores)
        invalidos = con.execute(
            f"SELECT evento_id, {nome} FROM _staging_eventos "
            f"WHERE {nome} IS NOT NULL AND {nome} NOT IN ({marcadores}) LIMIT 5",
            valores,
        ).fetchall()
        if invalidos:
            raise ValueError(f"Domínio inválido em {coluna}: {invalidos}")
    conflitos = con.execute(
        "SELECT evento_id, count(*) FROM (SELECT DISTINCT * FROM _staging_eventos) "
        "GROUP BY evento_id HAVING count(*) > 1 ORDER BY evento_id LIMIT 10"
    ).fetchall()
    if conflitos:
        raise ValueError(f"Conflito de evento_id: {conflitos}")


def executar() -> dict:
    if not db.BANCO.is_file():
        raise FileNotFoundError(f"Banco ausente: {db.BANCO}; execute pipeline.ingestao")
    con = db.conectar()
    try:
        existe = con.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'raw' AND table_name = 'eventos'"
        ).fetchall()
        if not existe:
            raise ValueError("raw.eventos ausente; execute pipeline.ingestao")
        con.execute("BEGIN")
        try:
            expressoes = _expressoes(con)
            con.execute(
                "CREATE TEMP TABLE _staging_eventos AS SELECT "
                + ", ".join(expressoes)
                + " FROM raw.eventos"
            )
            _validar_staging(con)
            entrada = con.execute("SELECT count(*) FROM _staging_eventos").fetchall()[0][0]
            db.criar_schema(con, "refined")
            con.execute(
                "CREATE OR REPLACE TABLE refined.eventos AS SELECT DISTINCT * FROM _staging_eventos"
            )
            con.execute("""
                CREATE OR REPLACE TABLE refined.evento_familia AS
                SELECT DISTINCT evento_id, trim(familia) AS familia_ocupacional
                FROM refined.eventos,
                     UNNEST(string_split(familias_ocupacionais, '; ')) AS partes(familia)
                WHERE trim(familia) <> ''
            """)
            orfaos = con.execute("""
                SELECT count(*) FROM refined.evento_familia AS f
                LEFT JOIN refined.eventos AS e ON e.evento_id = f.evento_id
                WHERE e.evento_id IS NULL
            """).fetchall()[0][0]
            if orfaos:
                raise ValueError(f"Associações sem evento: {orfaos}")
            eventos = con.execute("SELECT count(*) FROM refined.eventos").fetchall()[0][0]
            associacoes = con.execute("SELECT count(*) FROM refined.evento_familia").fetchall()[0][
                0
            ]
            consultas = [
                f"count(*) FILTER (WHERE {db.identificador(destino)} IS NULL)"
                for _, destino, _ in COLUNAS
            ]
            contagens = con.execute(
                "SELECT " + ", ".join(consultas) + " FROM refined.eventos"
            ).fetchall()[0]
            nulos = dict(zip((destino for _, destino, _ in COLUNAS), contagens, strict=True))
            con.execute("DROP TABLE _staging_eventos")
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
    finally:
        con.close()
    return {
        "entrada": entrada,
        "eventos": eventos,
        "associacoes": associacoes,
        "duplicatas_removidas": entrada - eventos,
        "nulos": nulos,
    }


def main():
    db.configurar_stdout()
    try:
        resumo = executar()
    except (OSError, ValueError, duckdb.Error) as exc:
        raise SystemExit(f"Erro na transformação: {exc}") from exc
    print(f"✓ refined.eventos: {resumo['eventos']:,} linhas".replace(",", "."))
    print(f"✓ refined.evento_familia: {resumo['associacoes']:,} linhas".replace(",", "."))
    print(f"Entrada: {resumo['entrada']}; duplicatas removidas: {resumo['duplicatas_removidas']}")
    print(f"Nulos preservados: {resumo['nulos']}")


if __name__ == "__main__":
    main()
