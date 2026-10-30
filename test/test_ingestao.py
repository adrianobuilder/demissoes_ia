"""CSV sintético; não lê raw/ nem o banco de produção."""

import csv
import io
from contextlib import redirect_stdout

import duckdb
import pytest

from pipeline import db, ingestao


def preparar(tmp_path, monkeypatch, linhas=(), colunas=None):
    arquivo = tmp_path / "entrada.csv"
    monkeypatch.setattr(ingestao, "ARQUIVO", arquivo)
    monkeypatch.setattr(db, "BANCO", tmp_path / "teste.duckdb")
    with arquivo.open("w", encoding="utf-8-sig", newline="") as saida:
        writer = csv.DictWriter(saida, fieldnames=colunas or ingestao.COLUNAS)
        writer.writeheader()
        writer.writerows(linhas)
    return arquivo


def test_texto_vazios_duplicatas_e_reexecucao(tmp_path, monkeypatch):
    linha = {"Company": "Árvore IA", "Event ID": "001", "Country": "NA"}
    preparar(tmp_path, monkeypatch, [linha, linha])
    assert ingestao.executar() == 2
    assert ingestao.executar() == 2
    with db.conectar(read_only=True) as con:
        assert con.execute(
            'SELECT "Company", "Event ID", "Country", "Date" FROM raw.eventos'
        ).fetchall() == [
            ("Árvore IA", "001", "NA", ""),
            ("Árvore IA", "001", "NA", ""),
        ]
        assert {r[1] for r in con.execute("DESCRIBE raw.eventos").fetchall()} == {"VARCHAR"}


def test_arquivo_ausente_nao_abre_banco(tmp_path, monkeypatch):
    arquivo = preparar(tmp_path, monkeypatch)
    arquivo.unlink()
    with pytest.raises(SystemExit, match="Erro na ingestão"):
        ingestao.main()
    assert not db.BANCO.exists()


def test_cabecalho_invalido_nao_abre_banco(tmp_path, monkeypatch):
    preparar(tmp_path, monkeypatch, colunas=["Company", "coluna extra"])
    with pytest.raises(SystemExit, match="Cabeçalho inválido"):
        ingestao.main()
    assert not db.BANCO.exists()


def test_cabecalho_duplicado_nao_e_renomeado(tmp_path, monkeypatch):
    arquivo = preparar(tmp_path, monkeypatch)
    arquivo.write_text("Company,Company\nAlfa,Beta\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicadas"):
        ingestao.executar()
    assert not db.BANCO.exists()


def test_utf8_invalido_nao_abre_banco(tmp_path, monkeypatch):
    arquivo = preparar(tmp_path, monkeypatch)
    arquivo.write_bytes(b"\xff\xfe\xff")
    with pytest.raises(SystemExit, match="Erro na ingestão"):
        ingestao.main()
    assert not db.BANCO.exists()


def test_entrada_vazia_tem_esquema_e_stdout(tmp_path, monkeypatch):
    preparar(tmp_path, monkeypatch)
    saida = io.StringIO()
    with redirect_stdout(saida):
        ingestao.main()
    assert "✓ raw.eventos: 0 linhas" in saida.getvalue()
    with db.conectar(read_only=True) as con:
        assert con.execute("SELECT count(*) FROM raw.eventos").fetchone() == (0,)
        assert len(con.execute("DESCRIBE raw.eventos").fetchall()) == 20


def test_rollback_preserva_carga_anterior(tmp_path, monkeypatch):
    preparar(tmp_path, monkeypatch, [{"Company": "Anterior"}])
    assert ingestao.executar() == 1
    preparar(tmp_path, monkeypatch, [{"Company": "Novo"}, {"Company": "Outro"}])
    gravar_original = db.gravar

    def falhar_depois_de_gravar(*args):
        gravar_original(*args)
        raise duckdb.InvalidInputException("falha sintética após escrita")

    monkeypatch.setattr(db, "gravar", falhar_depois_de_gravar)
    with pytest.raises(SystemExit, match="falha sintética"):
        ingestao.main()
    with db.conectar() as con:
        assert con.execute('SELECT "Company" FROM raw.eventos').fetchall() == [("Anterior",)]
