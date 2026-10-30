"""HTML determinístico e reutilização das figuras, sem banco nem CSV de produção."""

import ast
import io
import re
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import painel
import relatorio
from test.test_painel import dados_sinteticos

PROVENIENCIA = {"snapshot": "2030-01-01", "metodologia": "0.1"}
HORA = datetime(2030, 4, 5, 12, 0, tzinfo=relatorio.FUSO)


def test_sete_cartoes_quatro_faixas_ids_cdn_e_tamanho():
    html = relatorio.montar_html(dados_sinteticos(), HORA, PROVENIENCIA)
    assert re.findall(r'<p class="valor">([^<]+)</p>', html) == [
        "3",
        "2",
        "30",
        "40",
        "66,7%",
        "15,5",
        "1",
    ]
    assert re.findall(r'<section id="(faixa[0-9]+)"', html) == [
        "faixa01",
        "faixa02",
        "faixa03",
        "faixa04",
    ]
    assert re.findall(r'<div id="(g[0-9]+)"', html) == [f"g{i:02}" for i in range(1, 8)]
    assert html.count('src="https://cdn.plot.ly/') == 1
    assert html.count("Plotly.newPlot(") == 7
    assert 'lang="pt-BR"' in html and '<meta charset="utf-8">' in html
    assert len(html.encode("utf-8")) < 200 * 1024
    # Plotly escapa barras como \u002f dentro do JSON embutido no HTML.
    assert "jan/2024 a mar/2024" in html.replace(r"\u002f", "/")
    assert "Snapshot da fonte: 01/01/2030" in html
    assert "Dados de 05/04/2030 12:00" in html


def test_duas_geracoes_mudam_so_rodape():
    dados = dados_sinteticos()
    antes = relatorio.montar_html(dados, HORA, PROVENIENCIA)
    depois = relatorio.montar_html(dados, HORA + timedelta(minutes=1), PROVENIENCIA)
    assert antes != depois
    assert antes.replace("Dados de 05/04/2030 12:00", "Dados de 05/04/2030 12:01") == depois


def test_reutiliza_as_sete_funcoes_de_painel(monkeypatch):
    chamadas = []
    nomes = [
        "cortes_mensais",
        "postos_por_empresa",
        "eventos_por_atribuicao",
        "eventos_por_execucao",
        "eventos_por_familia",
        "eventos_por_evidencia",
        "concentracao_empresas",
    ]

    def rastrear(nome, original):
        def executar(dados):
            chamadas.append(nome)
            return original(dados)

        return executar

    for nome in nomes:
        monkeypatch.setattr(painel, nome, rastrear(nome, getattr(painel, nome)))
    assert relatorio.montar_html(dados_sinteticos(), HORA, PROVENIENCIA)
    assert chamadas == nomes


def test_main_escreve_em_tmp_path_relogio_controlado_e_stdout(tmp_path, monkeypatch):
    saida = tmp_path / "relatorio.html"
    monkeypatch.setattr(relatorio, "SAIDA", saida)
    monkeypatch.setattr(painel, "ler", dados_sinteticos)
    monkeypatch.setattr(painel, "proveniencia", lambda: PROVENIENCIA)

    class Relogio:
        @staticmethod
        def now(zona):
            assert zona.key == "America/Sao_Paulo"
            return HORA

    monkeypatch.setattr(relatorio, "datetime", Relogio)
    captura = io.StringIO()
    with redirect_stdout(captura):
        relatorio.main()
    assert str(saida.resolve()) in captura.getvalue()
    assert "Relatório:" in captura.getvalue() and " KB)" in captura.getvalue()
    assert "Dados de 05/04/2030 12:00" in saida.read_text(encoding="utf-8")


def test_falha_de_leitura_preserva_arquivo_anterior(tmp_path, monkeypatch):
    saida = tmp_path / "relatorio.html"
    saida.write_text("anterior", encoding="utf-8")
    monkeypatch.setattr(relatorio, "SAIDA", saida)

    def falhar():
        raise ValueError("mart sintético ausente")

    monkeypatch.setattr(painel, "ler", falhar)
    with pytest.raises(SystemExit, match="mart sintético ausente"):
        relatorio.main()
    assert saida.read_text(encoding="utf-8") == "anterior"


def test_limite_e_escape_de_textos(tmp_path, monkeypatch):
    prov = {**PROVENIENCIA, "metodologia": '<script>alert("x")</script>'}
    html = relatorio.montar_html(dados_sinteticos(), HORA, prov)
    assert "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in html
    saida = tmp_path / "relatorio.html"
    monkeypatch.setattr(relatorio, "SAIDA", saida)
    monkeypatch.setattr(painel, "ler", dados_sinteticos)
    monkeypatch.setattr(painel, "proveniencia", lambda: PROVENIENCIA)
    monkeypatch.setattr(relatorio, "montar_html", lambda *args: "x" * (200 * 1024))
    with pytest.raises(SystemExit, match="menos de 200 KB"):
        relatorio.main()
    assert not saida.exists()


def test_nao_importa_streamlit_nem_app():
    arvore = ast.parse(Path(relatorio.__file__).read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(arvore):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    assert "streamlit" not in imports and "app" not in imports
