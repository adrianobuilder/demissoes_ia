"""Leitura e figuras compartilhadas, com entradas sintéticas."""

import ast
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

import painel
from pipeline import db, marts
from test.test_marts import base


def dados_sinteticos():
    return {
        "kpis": pd.DataFrame(
            [
                {
                    "eventos_corte": 3,
                    "empresas_com_cortes": 2,
                    "postos_contabilizados": 30,
                    "postos_reportados_nao_contabilizados": 40,
                    "pct_cortes_quantificados": 66.7,
                    "mediana_postos_contabilizados": 15.5,
                    "declaracoes_sem_corte": 1,
                }
            ]
        ),
        "cortes_mensais": pd.DataFrame(
            {
                "mes": [date(2024, 3, 1), date(2024, 1, 1), date(2024, 2, 1)],
                "eventos_corte": [2, 1, 0],
                "eventos_quantificados": [1, 1, 0],
                "postos_contabilizados": [20, 10, None],
            }
        ),
        "empresas": pd.DataFrame(
            {
                "empresa": ["Alfa", "Beta"],
                "postos_contabilizados": [10, 20],
                "eventos_corte": [1, 2],
            }
        ),
        "atribuicao_ia": pd.DataFrame(
            {
                "atribuicao_ia": ["mixed", "blamed"],
                "eventos_corte": [2, 1],
                "pct_eventos": [66.7, 33.3],
            }
        ),
        "execucao_cortes": pd.DataFrame(
            {
                "situacao_execucao": ["executed", "announced"],
                "eventos_corte": [2, 1],
                "pct_eventos": [66.7, 33.3],
            }
        ),
        "familias_ocupacionais": pd.DataFrame(
            {"familia_ocupacional": ["Operações", "Engenharia"], "eventos_corte": [2, 2]}
        ),
        "evidencias": pd.DataFrame(
            {
                "nivel_evidencia": ["Tier 2", "Tier 1"],
                "eventos_corte": [2, 1],
                "pct_eventos": [66.7, 33.3],
            }
        ),
        "concentracao_empresas": pd.DataFrame(
            {
                "empresa": ["Alfa", "Beta"],
                "postos_contabilizados": [10, 20],
                "posicao": [2, 1],
                "pct_acumulado": [100, 66.67],
            }
        ),
    }


def test_formatadores_e_ausentes():
    assert painel.numero(12345) == "12.345"
    assert painel.numero(-1234.5, 1) == "-1.234,5"
    assert painel.pct(25.5) == "25,5%"
    assert painel.pct(0) == "0,0%"
    for valor in [None, float("nan"), pd.NA]:
        assert painel.numero(valor) == "—"
        assert painel.pct(valor) == "—"
    assert painel.mes_ano(date(2024, 2, 1)) == "fev/2024"
    assert painel.mes_ano(None) == "—"


def test_sete_cartoes_formatam_sem_recalcular():
    dados = dados_sinteticos()
    assert [c["valor"] for c in painel.cartoes(dados)] == [
        "3",
        "2",
        "30",
        "40",
        "66,7%",
        "15,5",
        "1",
    ]
    dados["kpis"].loc[0, "mediana_postos_contabilizados"] = 15.0
    assert painel.cartoes(dados)[5]["valor"] == "15"
    dados["kpis"] = dados["kpis"].iloc[:0]
    with pytest.raises(ValueError, match="exatamente uma linha"):
        painel.cartoes(dados)


def test_ler_marts_temporarios_e_libera_banco(tmp_path, monkeypatch):
    base(tmp_path, monkeypatch)
    marts.executar()
    dados = painel.ler(["kpis", "empresas"])
    assert list(dados) == ["kpis", "empresas"]
    assert dados["kpis"].iloc[0]["eventos_corte"] == 3
    with db.conectar() as con:
        con.execute("CREATE TABLE pode_escrever AS SELECT 1 AS n")
        assert con.execute("SELECT * FROM pode_escrever").fetchall() == [(1,)]


def test_ausencia_informa_todos_os_marts_e_fecha_conexao(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "BANCO", tmp_path / "teste.duckdb")
    with pytest.raises(FileNotFoundError):
        painel.ler(["kpis"])
    assert not db.BANCO.exists()
    with db.conectar() as con:
        con.execute("CREATE SCHEMA marts")
    monkeypatch.setattr(painel, "kpis", pd.DataFrame({"falso": [1]}), raising=False)
    with pytest.raises(ValueError, match="kpis, empresas"):
        painel.ler(["kpis", "empresas"])
    with db.conectar() as con:
        assert con.execute("SELECT 1").fetchall() == [(1,)]


def test_identificador_invalido_antes_da_conexao(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "BANCO", tmp_path / "ausente.duckdb")
    with pytest.raises(ValueError, match="inválido"):
        painel.ler(["kpis; DROP SCHEMA marts CASCADE"])
    assert not db.BANCO.exists()


def test_sete_figuras_preservam_dados_e_usam_valores_recebidos():
    dados = dados_sinteticos()
    antes = {nome: df.copy(deep=True) for nome, df in dados.items()}
    figuras = painel.figuras(dados)
    assert len(figuras) == 7
    assert [f.data[0].type for f in figuras] == [
        "bar",
        "pie",
        "bar",
        "bar",
        "pie",
        "bar",
        "scatter",
    ]
    assert list(figuras[1].data[0].values) == [2, 1]
    assert list(figuras[2].data[0].x) == [20, 10]
    assert list(figuras[3].data[0].y) == [2, 1]
    assert list(figuras[5].data[0].y) == ["Engenharia", "Operações"]
    assert [rotulo.replace("<br>", " ") for rotulo in figuras[4].data[0].labels] == [
        "Nível 1 · Fontes primárias",
        "Nível 2 · Jornalismo",
    ]
    assert list(figuras[6].data[0].x) == [1, 2]
    assert list(figuras[6].data[0].y) == [66.67, 100]
    assert figuras[6].layout.shapes[0].y0 == 80
    for figura in figuras:
        assert figura.layout.separators == ",."
    for nome in dados:
        pd.testing.assert_frame_equal(dados[nome], antes[nome])


def test_mensal_ordenacao_periodo_e_lacuna():
    figura = painel.cortes_mensais(dados_sinteticos()["cortes_mensais"])
    assert list(figura.data[0].x) == [date(2024, 1, 1), date(2024, 2, 1), date(2024, 3, 1)]
    assert pd.isna(figura.data[0].y[1])
    assert figura.data[0].type == "bar"
    assert "jan/2024 a mar/2024" in figura.layout.title.text
    assert list(figura.layout.xaxis.ticktext) == ["jan<br>2024", "mar<br>2024"]


def test_empresa_top_dez_desempate_e_nulos():
    dados = pd.DataFrame(
        {
            "empresa": [f"E{i:02}" for i in range(12, -1, -1)],
            "postos_contabilizados": [10] * 12 + [None],
        }
    )
    figura = painel.postos_por_empresa(dados)
    assert list(figura.data[0].y) == [f"E{i:02}" for i in range(1, 11)]
    assert len(figura.data[0].x) == 10


def test_figuras_sem_observacoes_e_concentracao_sem_denominador():
    dados = dados_sinteticos()
    vazios = {nome: df.iloc[:0] for nome, df in dados.items()}
    for figura in painel.figuras(vazios):
        assert len(figura.data) == 0
        assert figura.layout.annotations[0].text == "Sem observações para exibir"
    dados["concentracao_empresas"]["pct_acumulado"] = None
    assert len(painel.concentracao_empresas(dados["concentracao_empresas"]).data) == 0


def test_proveniencia_em_raiz_temporaria(tmp_path, monkeypatch):
    (tmp_path / "fontes").mkdir()
    (tmp_path / "fontes" / "proveniencia.json").write_text(
        '{"snapshot":"2030-01-01"}', encoding="utf-8"
    )
    monkeypatch.setattr(db, "RAIZ", tmp_path)
    assert painel.proveniencia() == {"snapshot": "2030-01-01"}


def test_painel_nao_importa_streamlit_nem_agrega_medidas():
    arvore = ast.parse(Path(painel.__file__).read_text(encoding="utf-8"))
    proibidas = {"groupby", "merge", "pivot", "pivot_table", "sum", "mean", "median", "agg"}
    assert not [n for n in ast.walk(arvore) if isinstance(n, ast.Attribute) and n.attr in proibidas]
    assert not [
        n
        for n in ast.walk(arvore)
        if isinstance(n, ast.Import) and any(a.name == "streamlit" for a in n.names)
    ]


def test_temas_preservam_valores_e_lacunas():
    dados = dados_sinteticos()
    claro = painel.figuras(dados, tema="claro")
    escuro = painel.figuras(dados, tema="escuro")
    assert len(claro) == len(escuro) == 7
    for figura_clara, figura_escura in zip(claro, escuro, strict=True):
        assert figura_clara.layout.paper_bgcolor == painel.TEMAS["claro"]["superficie"]
        assert figura_escura.layout.paper_bgcolor == painel.TEMAS["escuro"]["superficie"]
        for serie_clara, serie_escura in zip(figura_clara.data, figura_escura.data, strict=True):
            campos = (
                ("labels", "values", "customdata", "text")
                if serie_clara.type == "pie"
                else ("x", "y")
            )
            for campo in campos:
                if campo == "customdata":
                    assert serie_clara.customdata.tolist() == serie_escura.customdata.tolist()
                else:
                    pd.testing.assert_series_equal(
                        pd.Series(getattr(serie_clara, campo)),
                        pd.Series(getattr(serie_escura, campo)),
                    )
    assert pd.isna(escuro[0].data[0].y[1])
    assert escuro[6].layout.shapes[0].y0 == 80


def test_tema_invalido_tem_erro_claro():
    with pytest.raises(ValueError, match="Tema inválido"):
        painel.figuras(dados_sinteticos(), tema="inexistente")
    assert set(painel.TEMAS) == {"claro", "escuro"}


def test_pizzas_usam_populacao_exclusiva_e_percentuais_do_mart():
    dados = dados_sinteticos()
    dados["atribuicao_ia"].loc[0, "pct_eventos"] = 61.2
    figura = painel.eventos_por_atribuicao(dados["atribuicao_ia"])
    assert figura.data[0].hole == 0.68
    assert list(figura.data[0].values) == [2, 1]
    assert list(figura.data[0].text) == ["61,2%", "33,3%"]
    assert list(figura.data[0].customdata[:, 0]) == ["mixed", "blamed"]
    assert painel.eventos_por_familia(dados["familias_ocupacionais"]).data[0].type == "bar"
    zeros = dados["evidencias"].assign(eventos_corte=0)
    assert not painel.eventos_por_evidencia(zeros).data


def test_tabela_formata_top_cinco_sem_agregar_e_escapa_texto():
    dados = pd.DataFrame(
        {
            "empresa": [f"E{i}" for i in range(7)],
            "eventos_corte": [1] * 7,
            "postos_contabilizados": range(7),
        }
    )
    dados.loc[6, "empresa"] = "<script>"
    antes = dados.copy(deep=True)
    html = painel.tabela_empresas(dados)
    assert html.count("<tr>") == 6  # cabeçalho e cinco empresas
    assert "&lt;script&gt;" in html and "<script>" not in html
    assert "E0" not in html and "E1" not in html
    assert "<td>1</td><td>6</td>" in html
    pd.testing.assert_frame_equal(dados, antes)
