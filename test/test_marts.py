"""Executor e fórmulas SQL com cenários pequenos, sem consultar dados reais."""

import io
from contextlib import redirect_stdout
from datetime import date

import pytest

from pipeline import db, marts, transformacao
from test.test_transformacao import evento, preparar_raw


def base(tmp_path, monkeypatch):
    # E4 é declaração: seus 100 postos reportados não entram nos cartões de cortes.
    linhas = [
        evento(**{"Roles counted": "10", "Job families": "Engenharia; Operações"}),
        evento(
            **{
                "Event ID": "E2",
                "Date": "2024-03-01",
                "Roles reported (not counted)": "40",
                "Job families": "Operações",
                "Attribution": "blamed",
                "Execution": "executed",
                "Evidence tier": "Tier 2",
            }
        ),
        evento(
            **{
                "Event ID": "E3",
                "Date": "2024-03-02",
                "Company": "Beta",
                "Roles counted": "20",
                "Job families": "Engenharia",
                "Attribution": "explicit",
                "Execution": "executed",
                "Evidence tier": "Tier 2",
            }
        ),
        evento(
            **{
                "Event ID": "E4",
                "Company": "Gama",
                "Kind": "workforce statement",
                "Roles reported (not counted)": "100",
                "Job families": "Outra",
            }
        ),
    ]
    preparar_raw(tmp_path, monkeypatch, linhas)
    transformacao.executar()


def test_nove_marts_formulas_join_calendario_e_populacoes(tmp_path, monkeypatch):
    base(tmp_path, monkeypatch)
    saida = io.StringIO()
    with redirect_stdout(saida):
        marts.main()
    assert "Total: 9 marts" in saida.getvalue()
    assert "✓ marts.kpis: 1 linhas" in saida.getvalue()
    with db.conectar() as con:
        assert con.execute("SELECT * FROM marts.kpis").fetchall() == [(3, 2, 30, 40, 66.7, 15.0, 1)]
        assert con.execute("SELECT * FROM marts.cortes_mensais ORDER BY mes").fetchall() == [
            (date(2024, 1, 1), 1, 1, 10),
            (date(2024, 2, 1), 0, 0, None),
            (date(2024, 3, 1), 2, 1, 20),
        ]
        assert con.execute("SELECT * FROM marts.empresas ORDER BY empresa").fetchall() == [
            ("Alfa", 2, 1, 10),
            ("Beta", 1, 1, 20),
        ]
        assert con.execute("SELECT * FROM marts.familias_ocupacionais ORDER BY 1").fetchall() == [
            ("Engenharia", 2),
            ("Operações", 2),
        ]
        assert con.execute("SELECT * FROM marts.atribuicao_ia ORDER BY 1").fetchall() == [
            ("blamed", 1, 33.3),
            ("explicit", 1, 33.3),
            ("mixed", 1, 33.3),
        ]
        assert con.execute("SELECT * FROM marts.execucao_cortes ORDER BY 1").fetchall() == [
            ("announced", 1, 33.3),
            ("executed", 2, 66.7),
        ]
        assert con.execute("SELECT * FROM marts.evidencias ORDER BY 1").fetchall() == [
            ("Tier 1", 1, 33.3),
            ("Tier 2", 2, 66.7),
        ]
        assert con.execute(
            "SELECT empresa,posicao,pct_acumulado FROM marts.concentracao_empresas ORDER BY posicao"
        ).fetchall() == [("Beta", 1, 66.67), ("Alfa", 2, 100.0)]
        # JOIN expande para quatro associações de cortes, mas preserva três IDs.
        assert con.execute(
            "SELECT count(*),count(DISTINCT e.evento_id) FROM refined.eventos e JOIN refined.evento_familia f USING(evento_id) WHERE tipo_evento='cut'"
        ).fetchall() == [(4, 3)]
    assert marts.executar() == marts.executar()


def test_empresas_periodo_conta_eventos_sem_exigir_postos_e_separa_atribuicoes(
    tmp_path, monkeypatch
):
    base(tmp_path, monkeypatch)
    marts.executar()
    with db.conectar() as con:
        assert con.execute("""
            SELECT empresa,eventos_corte,ia_empregador,ia_entre_fatores,ia_outras_fontes,
                   eventos_periodo,ia_empregador_periodo,posicao_eventos,posicao_ia_empregador
            FROM marts.empresas_periodo WHERE tipo_periodo='total' ORDER BY empresa
        """).fetchall() == [("Alfa", 2, 0, 1, 1, 3, 1, 1, 2), ("Beta", 1, 1, 0, 0, 3, 1, 2, 1)]
        assert con.execute("""
            SELECT inicio_periodo,empresa,eventos_corte,ia_empregador
            FROM marts.empresas_periodo WHERE tipo_periodo='mes' ORDER BY 1,2
        """).fetchall() == [
            (date(2024, 1, 1), "Alfa", 1, 0),
            (date(2024, 3, 1), "Alfa", 1, 0),
            (date(2024, 3, 1), "Beta", 1, 1),
        ]
        # A declaração de Gama não entra; o evento de Alfa sem postos entra.
        assert con.execute(
            "SELECT DISTINCT empresa FROM marts.empresas_periodo ORDER BY 1"
        ).fetchall() == [("Alfa",), ("Beta",)]


def test_empresas_periodo_anos_empate_e_atribuicao_ausente(tmp_path, monkeypatch):
    preparar_raw(
        tmp_path,
        monkeypatch,
        [
            evento(**{"Event ID": "A", "Company": "Alfa", "Attribution": "explicit"}),
            evento(
                **{
                    "Event ID": "B",
                    "Company": "Beta",
                    "Date": "2025-01-01",
                    "Attribution": "explicit",
                }
            ),
            evento(**{"Event ID": "C", "Company": "Gama", "Date": "2024-02-01", "Attribution": ""}),
        ],
    )
    transformacao.executar()
    sql = (db.PASTA_SQL / "09_empresas_periodo.sql").read_text(encoding="utf-8")
    with db.conectar() as con:
        con.execute("CREATE TABLE periodos AS " + sql)
        assert con.execute("""
            SELECT empresa,posicao_eventos,posicao_ia_empregador,ia_nao_classificada
            FROM periodos WHERE tipo_periodo='total' ORDER BY empresa
        """).fetchall() == [("Alfa", 1, 1, 0), ("Beta", 2, 2, 0), ("Gama", 3, 3, 1)]
        assert con.execute(
            "SELECT inicio_periodo,eventos_periodo FROM periodos WHERE tipo_periodo='ano' ORDER BY 1"
        ).fetchall() == [(date(2024, 1, 1), 2), (date(2024, 1, 1), 2), (date(2025, 1, 1), 1)]
        assert con.execute("SELECT count(*) FROM periodos WHERE empresa='Gama'").fetchall() == [
            (3,)
        ]


def test_kpis_vazios_preservam_desconhecidos_e_denominador_zero(tmp_path, monkeypatch):
    preparar_raw(tmp_path, monkeypatch, [])
    transformacao.executar()
    sql = (db.PASTA_SQL / "02_kpis.sql").read_text(encoding="utf-8")
    with db.conectar() as con:
        assert con.execute(sql).fetchall() == [(0, 0, None, None, None, None, 0)]
    preparar_raw(tmp_path, monkeypatch, [evento()])
    transformacao.executar()
    with db.conectar() as con:
        assert con.execute(sql).fetchall() == [(1, 1, None, None, 0.0, None, 0)]


def test_pareto_desempata_e_protege_total_zero(tmp_path, monkeypatch):
    linhas = [
        evento(**{"Company": "Beta", "Roles counted": "10"}),
        evento(**{"Company": "Alfa", "Event ID": "E2", "Roles counted": "10"}),
    ]
    preparar_raw(tmp_path, monkeypatch, linhas)
    transformacao.executar()
    sql = (db.PASTA_SQL / "08_concentracao_empresas.sql").read_text(encoding="utf-8")
    with db.conectar() as con:
        assert con.execute(sql).fetchall() == [("Alfa", 10, 1, 50.0), ("Beta", 10, 2, 100.0)]
        con.execute("UPDATE refined.eventos SET postos_contabilizados=0")
        assert con.execute(sql).fetchall() == [("Alfa", 0, 1, None), ("Beta", 0, 2, None)]


def test_nomes_invalidos_e_colisoes_antes_do_banco(tmp_path, monkeypatch):
    pasta = tmp_path / "sql"
    pasta.mkdir()
    monkeypatch.setattr(marts, "PASTA_SQL", pasta)
    monkeypatch.setattr(db, "BANCO", tmp_path / "nao_criar.duckdb")
    with pytest.raises(SystemExit, match="Nenhum SQL"):
        marts.main()
    invalido = pasta / "sem_prefixo.sql"
    invalido.write_text("SELECT 1", encoding="utf-8")
    with pytest.raises(SystemExit, match="Nome inválido"):
        marts.main()
    invalido.unlink()
    (pasta / "01_Resumo.sql").write_text("SELECT 1", encoding="utf-8")
    (pasta / "02_resumo.sql").write_text("SELECT 2", encoding="utf-8")
    with pytest.raises(SystemExit, match="duplicado"):
        marts.main()
    assert not db.BANCO.exists()


def test_remocao_e_rollback_de_erro_vazio_e_multiplos_comandos(tmp_path, monkeypatch):
    base(tmp_path, monkeypatch)
    pasta = tmp_path / "sql"
    pasta.mkdir()
    monkeypatch.setattr(marts, "PASTA_SQL", pasta)
    primeiro = pasta / "01_um.sql"
    segundo = pasta / "02_dois.sql"
    primeiro.write_text(
        "-- comentário\nWITH base AS (SELECT 1 AS n) SELECT * FROM base;", encoding="utf-8"
    )
    segundo.write_text("SELECT 2 AS n", encoding="utf-8")
    assert marts.executar() == [("um", 1), ("dois", 1)]
    segundo.unlink()
    assert marts.executar() == [("um", 1)]
    with db.conectar() as con:
        assert con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='marts'"
        ).fetchall() == [("um",)]
    for sql in [
        "SELECT * FROM inexistente",
        "SELECT 3 WHERE FALSE",
        "SELECT 1; SELECT 2",
        "DELETE FROM refined.eventos",
    ]:
        primeiro.write_text("SELECT 9 AS n", encoding="utf-8")
        segundo.write_text(sql, encoding="utf-8")
        saida = io.StringIO()
        with redirect_stdout(saida), pytest.raises(SystemExit, match="02_dois.sql"):
            marts.main()
        assert "✓" not in saida.getvalue()
        with db.conectar() as con:
            assert con.execute("SELECT * FROM marts.um").fetchall() == [(1,)]
            assert con.execute("SELECT count(*) FROM refined.eventos").fetchall() == [(4,)]


def test_dependencias_e_banco_ausentes(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "BANCO", tmp_path / "ausente.duckdb")
    with pytest.raises(SystemExit, match="Banco ausente"):
        marts.main()
    assert not db.BANCO.exists()
    with db.conectar() as con:
        con.execute("CREATE SCHEMA refined")
    with pytest.raises(SystemExit, match="evento_familia.*eventos"):
        marts.main()
