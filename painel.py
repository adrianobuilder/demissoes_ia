"""Spec compartilhada do painel e do relatório.

Ler somente SELECT * dos oito marts, em conexão read-only curta e sem fallback
para objetos Python. Não importar Streamlit nem calcular medidas de negócio.
Formatar números brasileiros sem locale; ausentes são '—'.

Quatro faixas: sete cartões; mensal em largura inteira; empresa/atribuição/execução;
família/evidência/concentração. Sete figuras reutilizadas por app.py e relatorio.py.
O período padrão é o intervalo mensal completo; o filtro do app altera só a figura
mensal. Os cartões e as outras figuras representam o snapshot inteiro.

Ordenar, filtrar, top 10, traduções de rótulos e formatação são permitidos. Não
agregar, juntar ou criar indicadores em pandas. Funções de gráficos não alteram
seus DataFrames. Quantidade desconhecida mantém lacuna, com connectgaps=False.
"""

import json
import re
import textwrap
from html import escape

import duckdb
import pandas as pd
import plotly.graph_objects as go

from pipeline import db

MARTS = (
    "cortes_mensais",
    "kpis",
    "empresas",
    "atribuicao_ia",
    "execucao_cortes",
    "evidencias",
    "familias_ocupacionais",
    "concentracao_empresas",
)
COR = "#2563EB"
MESES = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
CARTOES = (
    ("eventos_corte", "Eventos de corte", "numero", "Somente eventos classificados como cut."),
    ("empresas_com_cortes", "Empresas com cortes", "numero", "Nomes distintos entre os cortes."),
    (
        "postos_contabilizados",
        "Postos contabilizados",
        "numero",
        "Aceitos pela metodologia da fonte; podem estar anunciados ou parcialmente executados.",
    ),
    (
        "postos_reportados_nao_contabilizados",
        "Postos não contabilizados",
        "numero",
        "Reportados em cortes, mas excluídos da contagem da fonte. Não somar ao cartão anterior.",
    ),
    (
        "pct_cortes_quantificados",
        "Cortes quantificados",
        "pct",
        "Cortes com quantidade contabilizada divididos por todos os cortes.",
    ),
    (
        "mediana_postos_contabilizados",
        "Mediana de postos",
        "mediana",
        "Somente eventos de corte com quantidade contabilizada conhecida.",
    ),
    (
        "declaracoes_sem_corte",
        "Declarações sem corte",
        "numero",
        "Workforce statements, fora da população de eventos de corte.",
    ),
)
TRADUCOES = {
    "explicit": "Empregador cita IA",
    "mixed": "IA entre os fatores",
    "blamed": "Atribuição de outra fonte",
    "announced": "Anunciado",
    "executed": "Executado",
    "partial": "Parcial",
    "reversed": "Revertido",
    "unknown": "Desconhecido",
}


def ler(marts=MARTS) -> dict[str, pd.DataFrame]:
    nomes = tuple(marts)
    for nome in nomes:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", nome):
            raise ValueError(f"Nome de mart inválido: {nome}")
    con = db.conectar(read_only=True)
    dados, faltantes = {}, []
    try:
        con.execute("SET python_enable_replacements = false")
        for nome in nomes:
            try:
                dados[nome] = con.execute(f"SELECT * FROM marts.{db.identificador(nome)}").df()
            except duckdb.CatalogException:
                faltantes.append(nome)
    finally:
        con.close()
    if faltantes:
        raise ValueError(f"Marts ausentes: {', '.join(faltantes)}; execute pipeline.marts")
    return dados


def proveniencia() -> dict:
    return json.loads((db.RAIZ / "fontes" / "proveniencia.json").read_text(encoding="utf-8"))


def numero(valor, casas=0) -> str:
    if pd.isna(valor):
        return "—"
    return f"{valor:,.{casas}f}".translate(str.maketrans({",": ".", ".": ","}))


def pct(valor, casas=1) -> str:
    if pd.isna(valor):
        return "—"
    return numero(valor, casas) + "%"


def mes_ano(valor) -> str:
    if pd.isna(valor):
        return "—"
    data = pd.Timestamp(valor)
    return f"{MESES[data.month - 1]}/{data.year}"


def cartoes(dados) -> list[dict[str, str]]:
    if len(dados["kpis"]) != 1:
        raise ValueError("marts.kpis deve ter exatamente uma linha")
    linha = dados["kpis"].iloc[0]
    resultado = []
    for campo, titulo, formato, ajuda in CARTOES:
        valor = linha[campo]
        if formato == "pct":
            texto = pct(valor)
        else:
            casas = (
                1
                if formato == "mediana" and pd.notna(valor) and not float(valor).is_integer()
                else 0
            )
            texto = numero(valor, casas)
        resultado.append({"titulo": titulo, "valor": texto, "ajuda": ajuda})
    return resultado


def _acabamento(fig, titulo, altura=680):
    fig.update_layout(
        template="plotly_white",
        title={"text": titulo, "x": 0, "xanchor": "left", "font_size": 17},
        font={"family": "Arial, sans-serif", "size": 13, "color": "#172033"},
        height=altura,
        margin={"l": 12, "r": 30, "t": 100, "b": 65},
        separators=",.",
        colorway=[COR],
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    fig.update_xaxes(automargin=True, gridcolor="#E8EDF3")
    fig.update_yaxes(automargin=True, gridcolor="#E8EDF3")
    return fig


def _vazio(titulo, altura=680):
    fig = _acabamento(go.Figure(), titulo, altura)
    fig.add_annotation(
        text="Sem observações para exibir",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
    )
    return fig


def _barras(dados, categoria, valor, titulo, unidade):
    if dados.empty:
        return _vazio(titulo)
    rotulos = [
        "<br>".join(textwrap.wrap(escape(TRADUCOES.get(str(v), str(v))), 24))
        for v in dados[categoria]
    ]
    extras = [categoria, valor]
    hover = f"%{{customdata[0]}}<br>{unidade}: %{{x:,.0f}}"
    if "pct_eventos" in dados.columns:
        extras.append("pct_eventos")
        hover += "<br>Participação: %{customdata[2]:.1f}%"
    fig = go.Figure(
        go.Bar(
            x=dados[valor],
            y=rotulos,
            orientation="h",
            marker_color=COR,
            text=[numero(v) for v in dados[valor]],
            textposition="outside",
            cliponaxis=False,
            customdata=dados[extras].to_numpy(),
            hovertemplate=hover + "<extra></extra>",
        )
    )
    _acabamento(fig, titulo)
    fig.update_xaxes(title_text=unidade, rangemode="tozero", tickformat=",.0f")
    fig.update_yaxes(
        autorange="reversed", title_text=None, categoryorder="array", categoryarray=rotulos
    )
    return fig


def cortes_mensais(dados):
    ordenado = dados.sort_values("mes")
    if ordenado.empty:
        return _vazio("01 · Postos contabilizados por mês", 380)
    periodo = f"{mes_ano(ordenado.iloc[0]['mes'])} a {mes_ano(ordenado.iloc[-1]['mes'])}"
    fig = go.Figure(
        go.Scatter(
            x=ordenado["mes"],
            y=ordenado["postos_contabilizados"],
            mode="lines+markers",
            line={"color": COR, "width": 2},
            marker={"size": 6},
            connectgaps=False,
            customdata=ordenado[["eventos_corte", "eventos_quantificados"]].to_numpy(),
            hovertemplate="%{x|%m/%Y}<br>Postos contabilizados: %{y:,.0f}"
            "<br>Eventos de corte: %{customdata[0]}"
            "<br>Eventos quantificados: %{customdata[1]}<extra></extra>",
        )
    )
    _acabamento(fig, f"01 · Postos contabilizados por mês<br><sup>{periodo}</sup>", 380)
    ticks = ordenado["mes"].iloc[::6].tolist()
    if ticks[-1] != ordenado.iloc[-1]["mes"]:
        ticks.append(ordenado.iloc[-1]["mes"])
    fig.update_xaxes(
        title_text=None, tickmode="array", tickvals=ticks, ticktext=[mes_ano(v) for v in ticks]
    )
    fig.update_yaxes(title_text="Postos contabilizados", rangemode="tozero", tickformat=",.0f")
    return fig


def postos_por_empresa(dados):
    ordenado = (
        dados.loc[dados["postos_contabilizados"].notna()]
        .sort_values(["postos_contabilizados", "empresa"], ascending=[False, True])
        .head(10)
    )
    return _barras(
        ordenado,
        "empresa",
        "postos_contabilizados",
        "03 · Empresas com mais postos<br><sup>Dez maiores totais contabilizados</sup>",
        "Postos contabilizados",
    )


def eventos_por_atribuicao(dados):
    ordenado = dados.sort_values(["eventos_corte", "atribuicao_ia"], ascending=[False, True])
    return _barras(
        ordenado,
        "atribuicao_ia",
        "eventos_corte",
        "04 · Atribuição à IA<br><sup>Classificação da fonte</sup>",
        "Eventos de corte",
    )


def eventos_por_execucao(dados):
    ordenado = dados.sort_values(["eventos_corte", "situacao_execucao"], ascending=[False, True])
    return _barras(
        ordenado,
        "situacao_execucao",
        "eventos_corte",
        "05 · Situação de execução",
        "Eventos de corte",
    )


def eventos_por_familia(dados):
    ordenado = dados.sort_values(["eventos_corte", "familia_ocupacional"], ascending=[False, True])
    return _barras(
        ordenado,
        "familia_ocupacional",
        "eventos_corte",
        "07 · Famílias ocupacionais<br><sup>Eventos podem aparecer em várias famílias</sup>",
        "Eventos distintos de corte",
    )


def eventos_por_evidencia(dados):
    return _barras(
        dados.sort_values("nivel_evidencia"),
        "nivel_evidencia",
        "eventos_corte",
        "06 · Nível de evidência<br><sup>Não equivale ao grau de atribuição à IA</sup>",
        "Eventos de corte",
    )


def concentracao_empresas(dados):
    ordenado = dados.sort_values("posicao")
    if ordenado.loc[ordenado["pct_acumulado"].notna()].empty:
        return _vazio("08 · Concentração por empresa")
    fig = go.Figure(
        go.Scatter(
            x=ordenado["posicao"],
            y=ordenado["pct_acumulado"],
            mode="lines",
            line={"color": COR, "width": 2},
            customdata=ordenado[["empresa", "postos_contabilizados"]].to_numpy(),
            hovertemplate="%{customdata[0]}<br>Posição: %{x}"
            "<br>Postos contabilizados: %{customdata[1]:,.0f}"
            "<br>Participação acumulada: %{y:.2f}%<extra></extra>",
        )
    )
    _acabamento(
        fig, "08 · Concentração por empresa<br><sup>Acumulado dos postos contabilizados</sup>"
    )
    fig.add_hline(y=80, line_dash="dash", line_color="#64748B")
    fig.update_xaxes(title_text="Posição da empresa", rangemode="tozero", tickformat=",.0f")
    fig.update_yaxes(title_text="Participação acumulada (%)", range=[0, 105])
    return fig


def figuras(dados):
    return [
        cortes_mensais(dados["cortes_mensais"]),
        postos_por_empresa(dados["empresas"]),
        eventos_por_atribuicao(dados["atribuicao_ia"]),
        eventos_por_execucao(dados["execucao_cortes"]),
        eventos_por_familia(dados["familias_ocupacionais"]),
        eventos_por_evidencia(dados["evidencias"]),
        concentracao_empresas(dados["concentracao_empresas"]),
    ]
