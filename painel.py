"""Spec compartilhada do painel e do relatório.

Ler somente SELECT * dos nove marts, em conexão read-only curta e sem fallback
para objetos Python. Não importar Streamlit nem calcular medidas de negócio.
Formatar números brasileiros sem locale; ausentes são '—'.

Cinco faixas: sete cartões; empresas por período; mensal/atribuição;
empresa/execução/evidência; família/concentração. Nove figuras compartilhadas.
No HTML: dois rankings; mensal, atribuição, postos por empresa, execução,
evidência, família e concentração. Colunas mensais/execução, rosca de atribuição,
pizza de evidência, barras horizontais e curva de concentração.
As sete figuras de figuras() mantêm o escopo anterior: filtro só no mensal.
figuras_empresas() recebe um único período do novo mart e retorna dois rankings
por eventos, sem exigir postos conhecidos. Filtros de ano/mês e de empresa
alteram apenas essa nova seção. Resumo e detalhe mensal vêm prontos do SQL;
nunca somar os níveis total/ano/mês. Empates dos rankings são alfabéticos.

Ordenar, filtrar, top 10, traduções de rótulos e formatação são permitidos. Não
agregar, juntar ou criar indicadores em pandas. Funções de gráficos não alteram
seus DataFrames. Quantidade desconhecida mantém lacuna, sem virar barra zero.
Pizzas usam contagens de categorias exclusivas; percentuais vêm do mart.
Famílias se sobrepõem e nunca são representadas como partes de uma pizza.

Composição de terminal financeiro: cabeçalho compacto, indicadores, painéis com
borda discreta, títulos de seção e tabela de consulta. Temas claro/escuro,
rótulos traduzidos e cores explícitas. A troca de tema não altera valores, filtros
ou o conjunto de figuras. O HTML mantém o tema claro por padrão.
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
    "empresas_periodo",
)
COR = "#2563EB"
TEMAS = {
    "claro": {
        "fundo": "#EDF1F5",
        "superficie": "#FFFFFF",
        "superficie_2": "#F7FAFF",
        "texto": "#182B45",
        "secundario": "#52657E",
        "borda": "#DDE5EF",
        "grade": "#E7EDF5",
        "acento": "#235C95",
        "acento_suave": "#EAF1FF",
        "sobre_acento": "#FFFFFF",
        "hero": "#102E57",
        "sombra": "none",
    },
    "escuro": {
        "fundo": "#0C1522",
        "superficie": "#131F2E",
        "superficie_2": "#1A2A3D",
        "texto": "#E4ECF8",
        "secundario": "#A4B5CD",
        "borda": "#2A3850",
        "grade": "#26354D",
        "acento": "#78B4FF",
        "acento_suave": "#1D3555",
        "sobre_acento": "#09162B",
        "hero": "#10274D",
        "sombra": "none",
    },
}
MESES = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
CARTOES = (
    (
        "eventos_corte",
        "Eventos de corte",
        "numero",
        "Registros de corte: um evento pode atingir várias pessoas. Não é a quantidade de pessoas demitidas.",
    ),
    ("empresas_com_cortes", "Empresas com cortes", "numero", "Nomes distintos entre os cortes."),
    (
        "postos_contabilizados",
        "Postos contabilizados",
        "numero",
        "Aceitos pela metodologia da fonte; podem estar anunciados ou parcialmente executados.",
    ),
    (
        "postos_reportados_nao_contabilizados",
        "Postos não contados",
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
    "Not specified": "Não especificado",
    "Software engineering and IT": "Engenharia de software e TI",
    "Corporate functions": "Funções corporativas",
    "Sales and marketing": "Vendas e marketing",
    "Customer service and support": "Atendimento e suporte",
    "Management layers": "Camadas de gestão",
    "Operations and back office": "Operações e apoio",
    "Product and design": "Produto e design",
    "Writing, editorial and translation": "Redação, edição e tradução",
    "Consulting and professional services": "Consultoria e serviços profissionais",
    "Content moderation": "Moderação de conteúdo",
    "Frontline and manual work": "Trabalho operacional e manual",
    "Tier 1": "Nível 1 · Fontes primárias",
    "Tier 2": "Nível 2 · Jornalismo",
    "Tier 3": "Nível 3 · Evidência limitada",
}
CORES_CATEGORIAS = {
    "claro": {
        "mixed": "#267CB8",
        "blamed": "#8EC8E9",
        "explicit": "#123E68",
        "Tier 1": "#123E68",
        "Tier 2": "#267CB8",
        "Tier 3": "#8EC8E9",
    },
    "escuro": {
        "mixed": "#56A8E4",
        "blamed": "#B7DDF4",
        "explicit": "#2A6BA3",
        "Tier 1": "#2A6BA3",
        "Tier 2": "#56A8E4",
        "Tier 3": "#B7DDF4",
    },
}


def paleta(tema="claro"):
    if tema not in TEMAS:
        raise ValueError(f"Tema inválido: {tema}")
    return TEMAS[tema]


def estilos(tema="claro"):
    variaveis = ";".join(f"--{nome}:{valor}" for nome, valor in paleta(tema).items())
    css = (db.RAIZ / "design" / "painel.css").read_text(encoding="utf-8")
    return f"<style>:root{{{variaveis}}}{css}</style>"


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


def _acabamento(fig, titulo, altura=340):
    fig.update_layout(
        template="plotly_white",
        title={"text": titulo, "x": 0, "xanchor": "left", "font_size": 12},
        font={"family": "Segoe UI, Arial, sans-serif", "size": 11, "color": "#182B45"},
        height=altura,
        margin={"l": 8, "r": 35, "t": 56, "b": 48},
        separators=",.",
        colorway=[COR],
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        bargap=0.32,
        barcornerradius=3,
    )
    fig.update_xaxes(automargin=True, gridcolor="#E8EDF3")
    fig.update_yaxes(automargin=True, gridcolor="#E8EDF3")
    return fig


def _vazio(titulo, altura=340):
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


def _barras(dados, categoria, valor, titulo, unidade, altura=355):
    if dados.empty:
        return _vazio(titulo, altura)
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
    _acabamento(fig, titulo, altura)
    fig.update_xaxes(title_text=unidade, rangemode="tozero", tickformat=",.0f")
    fig.update_yaxes(
        autorange="reversed",
        title_text=None,
        categoryorder="array",
        categoryarray=rotulos,
        showgrid=False,
    )
    return fig


def cortes_mensais(dados):
    ordenado = dados.sort_values("mes")
    if ordenado.empty:
        return _vazio("EVOLUÇÃO MENSAL", 310)
    periodo = f"{mes_ano(ordenado.iloc[0]['mes'])} a {mes_ano(ordenado.iloc[-1]['mes'])}"
    fig = go.Figure(
        go.Bar(
            x=ordenado["mes"],
            y=ordenado["postos_contabilizados"],
            marker_color=COR,
            customdata=ordenado[["eventos_corte", "eventos_quantificados"]].to_numpy(),
            hovertemplate="%{x|%m/%Y}<br>Postos contabilizados: %{y:,.0f}"
            "<br>Eventos de corte: %{customdata[0]}"
            "<br>Eventos quantificados: %{customdata[1]}<extra></extra>",
        )
    )
    _acabamento(fig, f"EVOLUÇÃO MENSAL<br><sup>Postos contabilizados · {periodo}</sup>", 310)
    # Até quatro datas legíveis também na largura de um celular; os dados
    # mensais completos continuam na curva e no hover.
    ultimo = len(ordenado) - 1
    indices = [0, ultimo] if ultimo < 3 else [0, ultimo // 3, 2 * ultimo // 3, ultimo]
    ticks = ordenado["mes"].iloc[sorted(set(indices))].tolist()
    fig.update_xaxes(
        title_text=None,
        tickmode="array",
        tickvals=ticks,
        ticktext=[mes_ano(v).replace("/", "<br>") for v in ticks],
        tickangle=0,
        showgrid=False,
    )
    fig.update_yaxes(title_text="Postos", rangemode="tozero", tickformat=",.0f", nticks=5)
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
        "MAIORES TOTAIS DE POSTOS<br><sup>Postos conhecidos · não é quantidade de eventos</sup>",
        "Postos contabilizados",
    )


def eventos_por_atribuicao(dados):
    ordenado = dados.sort_values(["eventos_corte", "atribuicao_ia"], ascending=[False, True])
    return _pizza(ordenado, "atribuicao_ia", "ATRIBUIÇÃO À IA", furo=0.68, altura=390)


def eventos_por_execucao(dados):
    ordenado = dados.sort_values(["eventos_corte", "situacao_execucao"], ascending=[False, True])
    if ordenado.empty:
        return _vazio("EXECUÇÃO DOS CORTES", 355)
    rotulos = [
        "<br>".join(textwrap.wrap(TRADUCOES.get(str(v), str(v)), 12))
        for v in ordenado["situacao_execucao"]
    ]
    figura = _acabamento(
        go.Figure(
            go.Bar(
                x=rotulos,
                y=ordenado["eventos_corte"],
                text=[numero(v) for v in ordenado["eventos_corte"]],
                textposition="outside",
                cliponaxis=False,
                marker_color=COR,
                customdata=ordenado[["situacao_execucao", "pct_eventos"]].to_numpy(),
                hovertemplate="%{x}<br>Eventos de corte: %{y:,.0f}<br>Participação: %{customdata[1]:.1f}%<extra></extra>",
            )
        ),
        "EXECUÇÃO DOS CORTES<br><sup>Situação informada pela fonte</sup>",
        355,
    )
    figura.update_xaxes(
        showgrid=False,
        tickangle=0,
        tickmode="array",
        tickvals=rotulos,
        ticktext=["Desconh." if v == "Desconhecido" else v for v in rotulos],
    )
    figura.update_yaxes(title_text="Eventos", rangemode="tozero", nticks=5, tickformat=",.0f")
    return figura


def _pizza(dados, categoria, titulo, furo=0, altura=355):
    if dados.empty or dados.loc[dados["eventos_corte"] > 0].empty:
        return _vazio(titulo, altura)
    rotulos = [
        "<br>".join(textwrap.wrap(TRADUCOES.get(str(v), str(v)), 27)) for v in dados[categoria]
    ]
    figura = _acabamento(
        go.Figure(
            go.Pie(
                labels=rotulos,
                values=dados["eventos_corte"],
                hole=furo,
                sort=False,
                direction="clockwise",
                rotation=20,
                text=[pct(v) for v in dados["pct_eventos"]],
                textinfo="text",
                textposition="inside",
                insidetextorientation="horizontal",
                textfont={"size": 12, "color": "#FFFFFF"},
                customdata=dados[[categoria, "eventos_corte", "pct_eventos"]].to_numpy(),
                marker={
                    "colors": [
                        CORES_CATEGORIAS["claro"].get(str(v), "#718096") for v in dados[categoria]
                    ],
                    "line": {"color": "#FFFFFF", "width": 2},
                },
                hovertemplate="%{label}<br>Eventos de corte: %{value:,.0f}<br>Participação: %{customdata[2]:.1f}%<extra></extra>",
            )
        ),
        titulo + "<br><sup>Participação nos eventos de corte</sup>",
        altura,
    )
    figura.update_layout(
        showlegend=True,
        margin={"l": 8, "r": 8, "t": 60, "b": 100},
        legend={
            "orientation": "h",
            "x": 0,
            "y": -0.1,
            "xanchor": "left",
            "yanchor": "top",
            "entrywidth": 1,
            "entrywidthmode": "fraction",
            "font_size": 11,
        },
        uniformtext={"minsize": 11, "mode": "hide"},
    )
    if furo:
        figura.add_annotation(
            text="ASSOCIAÇÃO<br>À IA",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={"size": 12},
        )
    return figura


def eventos_por_familia(dados):
    ordenado = dados.sort_values(["eventos_corte", "familia_ocupacional"], ascending=[False, True])
    figura = _barras(
        ordenado,
        "familia_ocupacional",
        "eventos_corte",
        "FAMÍLIAS OCUPACIONAIS<br><sup>Contagens sobrepostas · não somar</sup>",
        "Eventos distintos de corte",
        altura=455,
    )
    return figura


def eventos_por_evidencia(dados):
    return _pizza(
        dados.sort_values("nivel_evidencia"),
        "nivel_evidencia",
        "QUALIDADE DAS EVIDÊNCIAS",
    )


def concentracao_empresas(dados):
    ordenado = dados.sort_values("posicao")
    if ordenado.loc[ordenado["pct_acumulado"].notna()].empty:
        return _vazio("CONCENTRAÇÃO POR EMPRESA", 265)
    fig = go.Figure(
        go.Scatter(
            x=ordenado["posicao"],
            y=ordenado["pct_acumulado"],
            mode="lines",
            line={"color": COR, "width": 2},
            fill="tozeroy",
            fillcolor="rgba(38,124,184,0.10)",
            customdata=ordenado[["empresa", "postos_contabilizados"]].to_numpy(),
            hovertemplate="%{customdata[0]}<br>Posição: %{x}"
            "<br>Postos contabilizados: %{customdata[1]:,.0f}"
            "<br>Participação acumulada: %{y:.2f}%<extra></extra>",
        )
    )
    _acabamento(
        fig,
        "CONCENTRAÇÃO POR EMPRESA<br><sup>Participação acumulada nos postos conhecidos</sup>",
        265,
    )
    fig.add_hline(y=80, line_dash="dash", line_color="#64748B")
    fig.update_xaxes(
        title_text="Posição no ranking", rangemode="tozero", tickformat=",.0f", showgrid=False
    )
    fig.update_yaxes(title_text="Acumulado (%)", range=[0, 105], ticksuffix="%", nticks=5)
    return fig


def tabela_empresas(dados):
    """Cinco linhas para consulta; só ordena e formata o mart já agregado."""
    empresas = (
        dados.loc[dados["postos_contabilizados"].notna()]
        .sort_values(["postos_contabilizados", "empresa"], ascending=[False, True])
        .head(5)
    )
    linhas = "".join(
        f"<tr><td>{escape(str(linha.empresa))}</td><td>{numero(linha.eventos_corte)}</td>"
        f"<td>{numero(linha.postos_contabilizados)}</td></tr>"
        for linha in empresas.itertuples(index=False)
    )
    return (
        '<div class="company-table"><h3>TOP 5 POR POSTOS CONHECIDOS</h3>'
        "<table><thead><tr><th>Empresa</th><th>Eventos de corte</th><th>Postos</th></tr></thead>"
        f"<tbody>{linhas}</tbody></table></div>"
    )


def aplicar_tema(figura, tema="claro"):
    cores = paleta(tema)
    figura.update_layout(
        paper_bgcolor=cores["superficie"],
        plot_bgcolor=cores["superficie"],
        font_color=cores["texto"],
        title_font_color=cores["texto"],
        hoverlabel={
            "bgcolor": cores["superficie_2"],
            "font_color": cores["texto"],
            "bordercolor": cores["borda"],
        },
    )
    figura.update_xaxes(
        gridcolor=cores["grade"],
        zerolinecolor=cores["borda"],
        tickfont_color=cores["secundario"],
        title_font_color=cores["secundario"],
    )
    figura.update_yaxes(
        gridcolor=cores["grade"],
        zerolinecolor=cores["borda"],
        tickfont_color=cores["secundario"],
        title_font_color=cores["secundario"],
    )
    figura.update_traces(marker_color=cores["acento"], selector={"type": "bar"})
    figura.update_traces(
        line_color=cores["acento"],
        marker_color=cores["acento"],
        line_width=2.5,
        selector={"type": "scatter"},
    )
    for serie in figura.data:
        if serie.type == "pie":
            serie.marker.colors = [
                CORES_CATEGORIAS[tema].get(str(v[0]), cores["secundario"]) for v in serie.customdata
            ]
            serie.marker.line.color = cores["superficie"]
            # Percentuais permanecem legíveis nas três tonalidades da paleta.
            serie.textfont.color = [
                "#102E47"
                if str(v[0]) in ("blamed", "Tier 3")
                or (tema == "escuro" and str(v[0]) in ("mixed", "Tier 2"))
                else "#FFFFFF"
                for v in serie.customdata
            ]
    figura.update_layout(legend_font_color=cores["secundario"])
    for forma in figura.layout.shapes:
        forma.line.color = cores["secundario"]
    for anotacao in figura.layout.annotations:
        anotacao.font.color = cores["secundario"]
    return figura


def figuras(dados, tema="claro"):
    paleta(tema)
    prontas = [
        cortes_mensais(dados["cortes_mensais"]),
        eventos_por_atribuicao(dados["atribuicao_ia"]),
        postos_por_empresa(dados["empresas"]),
        eventos_por_execucao(dados["execucao_cortes"]),
        eventos_por_evidencia(dados["evidencias"]),
        eventos_por_familia(dados["familias_ocupacionais"]),
        concentracao_empresas(dados["concentracao_empresas"]),
    ]
    return [aplicar_tema(figura, tema) for figura in prontas]


def selecionar_periodo(dados, ano=None, mes=None):
    """Filtrar o nível já agregado no SQL, sem somar meses nem misturar níveis."""
    if mes is not None and ano is None:
        raise ValueError("Escolha um ano antes do mês")
    tipo = "mes" if mes is not None else "ano" if ano is not None else "total"
    filtro = dados["tipo_periodo"].eq(tipo)
    datas = pd.to_datetime(dados["inicio_periodo"])
    if ano is not None:
        filtro &= datas.dt.year.eq(ano)
    if mes is not None:
        filtro &= datas.dt.month.eq(mes)
    return dados.loc[filtro].copy()


def ranking_eventos_empresa(dados):
    ordenado = dados.loc[dados["eventos_corte"] > 0].sort_values("posicao_eventos").head(5)
    figura = _barras(
        ordenado,
        "empresa",
        "eventos_corte",
        "TOP 5 · MAIS EVENTOS DE CORTE",
        "Eventos de corte (registros)",
        altura=300,
    )
    figura.update_xaxes(dtick=1)
    if ordenado.empty:
        figura.layout.annotations[0].text = "Nenhum evento de corte<br>registrado neste período"
    return figura


def ranking_ia_empregador(dados):
    ordenado = dados.loc[dados["ia_empregador"] > 0].sort_values("posicao_ia_empregador").head(5)
    figura = _barras(
        ordenado,
        "empresa",
        "ia_empregador",
        "TOP 5 · EMPREGADOR CITOU IA",
        "Eventos com IA citada pelo empregador",
        altura=300,
    )
    figura.update_xaxes(dtick=1)
    if ordenado.empty:
        figura.layout.annotations[
            0
        ].text = "Sem eventos com IA citada<br>pelo empregador neste período"
    return figura


def figuras_empresas(dados, periodo="Todo o registro", tema="claro"):
    if len(dados[["tipo_periodo", "inicio_periodo"]].drop_duplicates()) > 1:
        raise ValueError("Ranking exige um único período; não misture total, anos ou meses")
    prontas = [ranking_eventos_empresa(dados), ranking_ia_empregador(dados)]
    for figura in prontas:
        figura.update_layout(
            title_text=figura.layout.title.text + f"<br><sup>{escape(periodo)}</sup>"
        )
        aplicar_tema(figura, tema)
    return prontas


def quadro_eventos(dados, mensal=False):
    """Selecionar/ordenar contagens prontas; nenhum cálculo ou pivô na tela."""
    colunas = {
        "empresa": "Empresa",
        "eventos_corte": "Eventos de corte",
        "ia_empregador": "Empregador citou IA",
        "ia_entre_fatores": "IA entre os motivos",
        "ia_outras_fontes": "Associação por outras fontes",
        "ia_nao_classificada": "Sem classificação",
    }
    ordem = ["inicio_periodo", "empresa"] if mensal else ["posicao_eventos"]
    ordenado = dados.sort_values(ordem).copy()
    quadro = ordenado[list(colunas)].rename(columns=colunas)
    if mensal:
        quadro.insert(0, "Mês do evento", ordenado["inicio_periodo"].map(mes_ano))
    return quadro.reset_index(drop=True)


def tabela_eventos_html(dados, mensal=False):
    titulo = "MESES COM EVENTOS REGISTRADOS" if mensal else "EVENTOS POR EMPRESA NO PERÍODO"
    return (
        f'<div class="company-table"><h3>{titulo}</h3><div class="event-table">'
        + quadro_eventos(dados, mensal=mensal).to_html(index=False, border=0, escape=True)
        + "</div></div>"
    )
