"""Transformação e relação evento-família com dados inteiramente inventados."""

import io
from contextlib import redirect_stdout
from datetime import date

import duckdb
import pandas as pd
import pytest

from pipeline import db, ingestao, transformacao


def evento(**campos):
    linha = dict.fromkeys(ingestao.COLUNAS, "")
    linha.update(
        {
            "Company": "Alfa",
            "Date": "2024-01-15",
            "Event ID": "E1",
            "Kind": "cut",
            "Evidence tier": "Tier 1",
            "Attribution": "mixed",
            "Execution": "announced",
            "Counts in US index": "no",
            "Job families": "Engenharia; Operações",
        }
    )
    linha.update(campos)
    return linha


def preparar_raw(tmp_path, monkeypatch, linhas):
    monkeypatch.setattr(db, "BANCO", tmp_path / "teste.duckdb")
    dados = pd.DataFrame(linhas, columns=ingestao.COLUNAS, dtype=str)
    with db.conectar() as con:
        db.criar_schema(con, "raw")
        db.gravar(con, "raw", "eventos", dados)


def test_tipos_nulos_textos_familias_e_raw_preservada(tmp_path, monkeypatch):
    linhas = [
        evento(
            **{
                "Roles counted": "10",
                "Country": "NA",
                "Counts in US index": "yes",
                "Job families": "Engenharia; Operações; Engenharia; ",
            }
        ),
        evento(
            **{
                "Event ID": "E2",
                "Company": " Beta ",
                "Kind": "workforce statement",
                "Job families": "Engenharia",
                "Why not counted": "   ",
            }
        ),
    ]
    preparar_raw(tmp_path, monkeypatch, linhas)
    resumo = transformacao.executar()
    assert resumo["eventos"] == 2
    assert resumo["associacoes"] == 3
    assert resumo["nulos"]["postos_contabilizados"] == 1
    assert resumo["nulos"]["motivo_nao_contabilizado"] == 2
    assert transformacao.executar() == resumo
    with db.conectar() as con:
        tipos = {r[0]: r[1] for r in con.execute("DESCRIBE refined.eventos").fetchall()}
        assert len(tipos) == 20
        assert tipos["data_evento"] == "DATE"
        assert tipos["postos_contabilizados"] == "BIGINT"
        assert tipos["conta_indice_eua"] == "BOOLEAN"
        assert con.execute(
            "SELECT data_evento, postos_contabilizados, conta_indice_eua, pais_informado FROM refined.eventos WHERE evento_id='E1'"
        ).fetchall() == [(date(2024, 1, 15), 10, True, "NA")]
        assert con.execute(
            "SELECT empresa, postos_contabilizados FROM refined.eventos WHERE evento_id='E2'"
        ).fetchall() == [(" Beta ", None)]
        assert con.execute(
            'SELECT "Why not counted" FROM raw.eventos WHERE "Event ID"=\'E2\''
        ).fetchall() == [("   ",)]
        assert con.execute("SELECT * FROM refined.evento_familia ORDER BY 1,2").fetchall() == [
            ("E1", "Engenharia"),
            ("E1", "Operações"),
            ("E2", "Engenharia"),
        ]
        assert con.execute(
            "SELECT count(*) FROM refined.evento_familia f LEFT JOIN refined.eventos e USING(evento_id) WHERE e.evento_id IS NULL"
        ).fetchall() == [(0,)]


def test_remove_so_duplicata_integral_e_rejeita_conflito(tmp_path, monkeypatch):
    preparar_raw(tmp_path, monkeypatch, [evento(), evento()])
    assert transformacao.executar()["duplicatas_removidas"] == 1
    preparar_raw(tmp_path, monkeypatch, [evento(), evento(Company="Outro conteúdo")])
    with pytest.raises(SystemExit, match="Conflito de evento_id"):
        transformacao.main()
    with db.conectar() as con:
        assert con.execute("SELECT empresa FROM refined.eventos").fetchall() == [("Alfa",)]
        assert con.execute("SELECT count(*) FROM refined.evento_familia").fetchall() == [(2,)]
        assert con.execute("SELECT count(*) FROM raw.eventos").fetchall() == [(2,)]


def test_entradas_invalidas_preservam_as_duas_tabelas(tmp_path, monkeypatch):
    preparar_raw(tmp_path, monkeypatch, [evento()])
    transformacao.executar()
    casos = [
        {"Date": "2024-02-30"},
        {"Date": "2024-1-1"},
        {"Roles counted": "1.5"},
        {"Roles counted": "-2"},
        {"Roles counted": "999999999999999999999999"},
        {"Counts in US index": "talvez"},
        {"Counts in US index": ""},
        {"Kind": "outro"},
        {"Attribution": "nova"},
        {"Evidence tier": "Tier 4"},
        {"Execution": "nova"},
        {"Event ID": " "},
        {"Company": ""},
        {"Date": ""},
    ]
    for campos in casos:
        preparar_raw(tmp_path, monkeypatch, [evento(**campos)])
        with pytest.raises(SystemExit, match="Erro na transformação"):
            transformacao.main()
        with db.conectar() as con:
            assert con.execute("SELECT empresa FROM refined.eventos").fetchall() == [("Alfa",)]
            assert con.execute("SELECT count(*) FROM refined.evento_familia").fetchall() == [(2,)]


def test_rollback_depois_de_substituir_eventos(tmp_path, monkeypatch):
    preparar_raw(tmp_path, monkeypatch, [evento()])
    transformacao.executar()
    preparar_raw(tmp_path, monkeypatch, [evento(Company="Novo")])
    # Um objeto de tipo errado no destino do filho causa erro SQL real somente
    # depois de o pai ter sido substituído dentro da transação.
    with db.conectar() as con:
        con.execute("DROP TABLE refined.evento_familia")
        con.execute("""
            CREATE VIEW refined.evento_familia AS
            SELECT * FROM (VALUES ('E1', 'Engenharia'), ('E1', 'Operações'))
            AS pares(evento_id, familia_ocupacional)
        """)
    with pytest.raises(SystemExit, match="Erro na transformação"):
        transformacao.main()
    with db.conectar() as con:
        assert con.execute("SELECT empresa FROM refined.eventos").fetchall() == [("Alfa",)]
        assert con.execute("SELECT count(*) FROM refined.evento_familia").fetchall() == [(2,)]


@pytest.mark.parametrize(
    ("erro", "erro_esperado"),
    [
        (ValueError, SystemExit),
        (duckdb.InvalidInputException, SystemExit),
        (RuntimeError, RuntimeError),
    ],
)
def test_falha_no_resumo_reverte_ambas_as_tabelas(tmp_path, monkeypatch, erro, erro_esperado):
    preparar_raw(tmp_path, monkeypatch, [evento()])
    transformacao.executar()
    preparar_raw(tmp_path, monkeypatch, [evento(Company="Novo", **{"Job families": "Vendas"})])

    def falhar_no_resumo(con, entrada):
        # As duas escritas ocorreram; nenhuma pode persistir antes do commit.
        assert con.execute("SELECT empresa FROM refined.eventos").fetchall() == [("Novo",)]
        assert con.execute("SELECT * FROM refined.evento_familia").fetchall() == [("E1", "Vendas")]
        raise erro("falha após materializar as duas tabelas")

    monkeypatch.setattr(transformacao, "_resumir", falhar_no_resumo)
    saida = io.StringIO()
    with redirect_stdout(saida), pytest.raises(erro_esperado, match="falha após materializar"):
        transformacao.main()
    assert saida.getvalue() == ""
    with db.conectar() as con:
        assert con.execute("SELECT empresa FROM refined.eventos").fetchall() == [("Alfa",)]
        assert con.execute("SELECT * FROM refined.evento_familia ORDER BY 2").fetchall() == [
            ("E1", "Engenharia"),
            ("E1", "Operações"),
        ]
        assert con.execute('SELECT "Company" FROM raw.eventos').fetchall() == [("Novo",)]


def test_vazio_mantem_tipos_e_contagens_zero(tmp_path, monkeypatch):
    preparar_raw(tmp_path, monkeypatch, [])
    saida = io.StringIO()
    with redirect_stdout(saida):
        transformacao.main()
    assert "refined.eventos: 0 linhas" in saida.getvalue()
    assert "refined.evento_familia: 0 linhas" in saida.getvalue()
    with db.conectar() as con:
        assert con.execute("SELECT count(*) FROM refined.eventos").fetchall() == [(0,)]
        assert con.execute("SELECT count(*) FROM refined.evento_familia").fetchall() == [(0,)]
        assert {r[0]: r[1] for r in con.execute("DESCRIBE refined.eventos").fetchall()}[
            "data_evento"
        ] == "DATE"


def test_banco_e_raw_ausentes_tem_erro_controlado(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "BANCO", tmp_path / "ausente.duckdb")
    with pytest.raises(SystemExit, match="Banco ausente"):
        transformacao.main()
    assert not db.BANCO.exists()
    with db.conectar() as con:
        con.execute("CREATE SCHEMA raw")
    with pytest.raises(SystemExit, match="raw.eventos ausente"):
        transformacao.main()
