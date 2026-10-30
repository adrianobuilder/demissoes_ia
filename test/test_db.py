"""Regras da infraestrutura com banco real temporário."""

import duckdb
import pandas as pd
import pytest

from pipeline import db


def test_caminhos_absolutos_do_projeto():
    assert db.BANCO.is_absolute()
    assert db.BANCO.name == "demissao_ia.duckdb"
    assert db.ARQUIVO_RAW.parent.parent == db.RAIZ


def test_grava_substitui_e_delimita_identificadores(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "BANCO", tmp_path / "teste.duckdb")
    with db.conectar() as con:
        db.criar_schema(con, 'um"schema')
        dados = pd.DataFrame({'campo"texto': ["001", "NA", ""]})
        assert db.gravar(con, 'um"schema', "tabela com espaço", dados) == 3
        consulta = 'SELECT * FROM "um""schema"."tabela com espaço"'
        assert con.execute(consulta).fetchall() == [("001",), ("NA",), ("",)]
        assert db.gravar(con, 'um"schema', "tabela com espaço", dados.head(1)) == 1
        assert con.execute(consulta).fetchall() == [("001",)]
        assert db.gravar(con, 'um"schema', "tabela com espaço", dados.head(0)) == 0


def test_identificador_invalido():
    for nome in ["", "texto\x00"]:
        with pytest.raises(ValueError, match="Identificador"):
            db.identificador(nome)
    assert db.identificador('a"b') == '"a""b"'


def test_leitura_nao_cria_banco_e_fecha_conexao(tmp_path, monkeypatch):
    caminho = tmp_path / "teste.duckdb"
    monkeypatch.setattr(db, "BANCO", caminho)
    with pytest.raises(FileNotFoundError, match="ausente"):
        db.conectar(read_only=True)
    assert not caminho.exists()
    with db.conectar() as con:
        con.execute("CREATE TABLE inicial AS SELECT 1 AS numero")
    with db.conectar(read_only=True) as con:
        assert con.execute("SELECT * FROM inicial").fetchall() == [(1,)]
    with db.conectar() as con:
        assert con.execute("SELECT count(*) FROM inicial").fetchone() == (1,)


def test_desregistra_dataframe_apos_erro(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "BANCO", tmp_path / "teste.duckdb")
    with db.conectar() as con:
        db.criar_schema(con, "raw")
    with db.conectar(read_only=True) as con:
        with pytest.raises(duckdb.Error):
            db.gravar(con, "raw", "dados", pd.DataFrame({"a": [1]}))
        with pytest.raises(duckdb.CatalogException):
            con.execute("SELECT * FROM _entrada_dataframe")
