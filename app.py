"""Painel de composição financeira; spec em painel.py e design/visual.md.

Sete cartões, nove figuras compartilhadas e cinco faixas. A seção de empresas
tem filtros de ano/mês e consulta por empresa; os cartões mantêm o registro
completo. O filtro mensal anterior mantém seu próprio escopo.
Executar: uv run streamlit run app.py.
"""

from datetime import date
from html import escape

import duckdb
import pandas as pd
import streamlit as st

import painel

st.set_page_config(page_title="Registro de demissões · IA", page_icon="📊", layout="wide")


@st.cache_data(show_spinner=False)
def carregar():
    return painel.ler(), painel.proveniencia()


def grafico(indice):
    st.plotly_chart(
        figuras[indice],
        width="stretch",
        key=f"g{indice + 1:02}",
        theme=None,
        config={"displaylogo": False, "displayModeBar": False},
    )


def divisao(numero, titulo, detalhe, ancora):
    st.html(
        f'<div class="section-rule" id="{ancora}"><h2><span>{numero}</span> '
        f"{escape(titulo)}</h2><p>{escape(detalhe)}</p></div>"
    )


with st.container(key="topbar"), st.container(key="estrutura_cabecalho"):
    marca, navegacao, acoes = st.columns(3, vertical_alignment="center")
    with marca:
        st.html("""<div class="masthead"><span class="brand-mark">IA</span>
<div class="brand-name">TRABALHO &amp; TECNOLOGIA<small>DATA INTELLIGENCE / REGISTRO DE DEMISSÕES</small></div></div>""")
    with navegacao:
        st.html("""<nav class="header-nav" aria-label="Seções do painel">
<a href="#empresas">EMPRESAS</a><a href="#evolucao">PANORAMA</a>
<a href="#distribuicao">DISTRIBUIÇÃO</a></nav>""")
    with acoes, st.container(key="acoes_cabecalho"):
        aparencia, recarga = st.columns([1.65, 1], vertical_alignment="center")
        with aparencia, st.container(key="alternar_tema"):
            escolhido = st.segmented_control(
                "Aparência",
                ["Claro", "Escuro"],
                default="Claro",
                required=True,
                key="tema_visual",
                label_visibility="collapsed",
                width="stretch",
                format_func=lambda valor: f"☀ {valor}" if valor == "Claro" else f"☾ {valor}",
            )
        with recarga:
            if st.button(
                "Atualizar",
                icon=":material/refresh:",
                width="stretch",
                help="Reler os marts; não baixa outra versão da fonte.",
            ):
                carregar.clear()

tema = "escuro" if escolhido == "Escuro" else "claro"
st.html(painel.estilos(tema))

try:
    dados, fonte = carregar()
    cartoes = painel.cartoes(dados)
    snapshot = date.fromisoformat(fonte["snapshot"]).strftime("%d/%m/%Y")
except (OSError, ValueError, KeyError, duckdb.Error) as exc:
    st.error(
        f"Não foi possível ler os indicadores: {exc}. Execute uv run python -m pipeline.marts."
    )
    st.stop()

st.html(f"""<div class="page-heading" id="panorama"><div>
<p class="breadcrumb">OBSERVATÓRIO / INTELIGÊNCIA ARTIFICIAL</p>
<h1>Registro de demissões associadas à IA</h1>
<p>Eventos de corte, quantidades conhecidas e evidências da associação à inteligência artificial.</p>
</div><div class="snapshot"><span>SNAPSHOT DA FONTE</span><strong>{snapshot}</strong>
<small>Metodologia v{escape(str(fonte["metodologia"]))}</small></div></div>""")

with st.container(key="indicadores"):
    with st.container(key="kpis_principais"):
        icones = (
            ":material/event_note:",
            ":material/domain:",
            ":material/badge:",
            ":material/filter_alt_off:",
        )
        for coluna, cartao, icone in zip(st.columns(4), cartoes[:4], icones, strict=True):
            coluna.metric(cartao["titulo"], cartao["valor"], help=cartao["ajuda"], icon=icone)
    with st.container(key="kpis_complementares"):
        for coluna, cartao in zip(st.columns(3), cartoes[4:], strict=True):
            coluna.metric(cartao["titulo"], cartao["valor"], help=cartao["ajuda"])

divisao(
    "01",
    "QUAIS EMPRESAS MAIS REGISTRARAM CORTES?",
    "Filtre por ano e mês; consulte uma empresa",
    "empresas",
)
with st.container(key="empresas_periodo"):
    st.html("""<div class="reading-guide"><strong>Como ler:</strong> 5 eventos de corte significam
5 registros de corte, não 5 pessoas demitidas. O ranking da direita conta somente registros em
que o <strong>empregador citou IA</strong>; isso não prova que IA foi o motivo exclusivo.
<small>Os filtros desta seção não alteram os cartões do topo nem os demais gráficos.</small></div>""")
    base_empresas = dados["empresas_periodo"]
    anos = sorted(
        pd.to_datetime(base_empresas.loc[base_empresas["tipo_periodo"].eq("ano"), "inicio_periodo"])
        .dt.year.drop_duplicates()
        .tolist(),
        reverse=True,
    )
    with st.container(key="filtros_empresas"):
        coluna_ano, coluna_mes, coluna_empresa = st.columns([1, 1, 2])
        with coluna_ano:
            ano_opcao = st.selectbox(
                "Ano dos eventos",
                ["Todo o registro", *anos],
                format_func=str,
                key="ano_eventos_empresa",
            )
            ano_empresa = None if ano_opcao == "Todo o registro" else ano_opcao
        with coluna_mes:
            mes_opcao = st.selectbox(
                "Mês dos eventos",
                ["Todos os meses", *range(1, 13)]
                if ano_empresa is not None
                else ["Todos os meses"],
                format_func=lambda valor: (
                    valor if isinstance(valor, str) else painel.MESES[valor - 1]
                ),
                disabled=ano_empresa is None,
                key="mes_eventos_empresa",
            )
            mes_empresa = None if mes_opcao == "Todos os meses" else mes_opcao
        resumo_empresas = painel.selecionar_periodo(base_empresas, ano_empresa, mes_empresa)
        with coluna_empresa:
            empresa_opcao = st.selectbox(
                "Empresa para consultar (somente tabelas)",
                ["Todas as empresas", *sorted(resumo_empresas["empresa"].tolist())],
                key="empresa_eventos_consulta",
            )
            empresa_consulta = None if empresa_opcao == "Todas as empresas" else empresa_opcao
    periodo_empresa = (
        "Todo o registro"
        if ano_empresa is None
        else (
            f"{painel.MESES[mes_empresa - 1]}/{ano_empresa}"
            if mes_empresa is not None
            else f"Ano de {ano_empresa}"
        )
    )
    if resumo_empresas.empty:
        st.info(f"{periodo_empresa}: nenhum evento de corte registrado na base neste período.")
    else:
        periodo_dados = resumo_empresas.iloc[0]
        st.html(
            f'<div class="period-summary"><strong>{escape(periodo_empresa)}</strong> · '
            f"{painel.numero(periodo_dados['eventos_periodo'])} eventos de corte · "
            f"em {painel.numero(periodo_dados['ia_empregador_periodo'])} o empregador citou IA "
            "<span>Datas dos eventos; anúncios também podem estar incluídos.</span></div>"
        )
    novas_figuras = painel.figuras_empresas(resumo_empresas, periodo_empresa, tema=tema)
    with st.container(key="rankings_empresas"):
        for coluna, figura, chave in zip(
            st.columns(2), novas_figuras, ("todos", "ia"), strict=True
        ):
            with coluna, st.container(key=f"painel_ranking_{chave}"):
                st.plotly_chart(
                    figura,
                    width="stretch",
                    key=f"ranking_{chave}",
                    theme=None,
                    config={"displaylogo": False, "displayModeBar": False},
                )
    st.caption(
        "Até 5 empresas em cada gráfico. Empates ordenados pelo nome; veja todas as empresas na tabela. A consulta de empresa filtra apenas as tabelas."
    )
    meses_empresas = base_empresas.loc[base_empresas["tipo_periodo"].eq("mes")]
    datas_empresas = pd.to_datetime(meses_empresas["inicio_periodo"])
    if ano_empresa is not None:
        meses_empresas = meses_empresas.loc[datas_empresas.dt.year.eq(ano_empresa)]
    if mes_empresa is not None:
        meses_empresas = meses_empresas.loc[
            pd.to_datetime(meses_empresas["inicio_periodo"]).dt.month.eq(mes_empresa)
        ]
    resumo_consulta = resumo_empresas
    if empresa_consulta is not None:
        resumo_consulta = resumo_consulta.loc[resumo_consulta["empresa"].eq(empresa_consulta)]
        meses_empresas = meses_empresas.loc[meses_empresas["empresa"].eq(empresa_consulta)]
    resumo_tab, meses_tab = st.tabs(["Resumo por empresa", "Mês a mês por empresa"])
    with resumo_tab:
        st.html(painel.tabela_eventos_html(resumo_consulta))
    with meses_tab:
        st.html(painel.tabela_eventos_html(meses_empresas, mensal=True))
        st.caption(
            "A lista mostra somente meses com eventos registrados. Cada linha é uma empresa em um mês; não some o resumo com o detalhe mensal."
        )
    st.html(
        '<p class="panel-note"><b>Vínculo com IA:</b> “Empregador citou IA” = declaração do empregador; '
        "“IA entre os motivos” = associação a vários fatores; “Outras fontes” = atribuição por outra fonte. "
        "Nenhuma dessas categorias comprova causa exclusiva. Os números são registros, não pessoas.</p>"
    )

divisao("02", "PANORAMA DOS CORTES", "Evolução e composição do registro", "evolucao")
mensal = dados["cortes_mensais"]
meses = [pd.Timestamp(mes).date() for mes in mensal["mes"].sort_values()]
if not meses:
    st.error("O mart mensal está vazio. Reconstrua os indicadores.")
    st.stop()

with st.container(key="faixa_panorama"):
    evolucao, atribuicao = st.columns([2, 1])
    with evolucao, st.container(key="painel_mensal"):
        with st.container(key="filtro_periodo"):
            if len(meses) > 1:
                inicio, fim = st.select_slider(
                    "Período · filtra somente a evolução mensal",
                    options=meses,
                    value=(meses[0], meses[-1]),
                    format_func=painel.mes_ano,
                )
            else:
                inicio = fim = meses[0]
                st.caption(f"Período mensal: {painel.mes_ano(inicio)}")
        recorte = mensal.loc[
            (mensal["mes"] >= pd.Timestamp(inicio)) & (mensal["mes"] <= pd.Timestamp(fim))
        ]
        figuras = painel.figuras({**dados, "cortes_mensais": recorte}, tema=tema)
        grafico(0)
        st.html(
            '<p class="panel-note">Mês sem quantidade conhecida fica sem barra. O hover informa cada mês.</p>'
        )
    with atribuicao, st.container(key="painel_atribuicao"):
        grafico(1)
        st.html(
            '<p class="panel-note">Associação à IA não comprova causalidade. Cada corte pertence a uma classificação.</p>'
        )

divisao(
    "03",
    "DISTRIBUIÇÃO E EVIDÊNCIAS",
    "Snapshot completo · independe do filtro mensal",
    "distribuicao",
)
with st.container(key="faixa_distribuicao"):
    for coluna, indice, chave in zip(
        st.columns(3), (2, 3, 4), ("empresas", "execucao", "evidencias"), strict=True
    ):
        with coluna, st.container(key=f"painel_{chave}"):
            grafico(indice)
            notas = {
                "empresas": "Somente empresas com quantidade contabilizada conhecida.",
                "execucao": "Postos contabilizados podem estar anunciados ou parcialmente executados.",
                "evidencias": "Percentuais arredondados. Nível de evidência difere da atribuição à IA.",
            }
            st.html(f'<p class="panel-note">{notas[chave]}</p>')

divisao(
    "04",
    "OCUPAÇÕES E CONCENTRAÇÃO",
    "Famílias sobrepostas e distribuição dos postos conhecidos",
    "ocupacoes",
)
with st.container(key="faixa_ocupacoes"):
    familias, concentracao = st.columns([1.25, 1])
    with familias, st.container(key="painel_familias"):
        grafico(5)
        st.html(
            '<p class="panel-note">Um evento pode citar várias famílias ocupacionais. As contagens não são aditivas.</p>'
        )
    with concentracao:
        with st.container(key="painel_concentracao"):
            grafico(6)
        with st.container(key="painel_tabela"):
            st.html(painel.tabela_empresas(dados["empresas"]))

with st.expander("Metodologia e como interpretar os indicadores", icon=":material/info:"):
    st.markdown("""
- **Postos contabilizados:** aceitos pela metodologia da fonte, incluindo anúncios e execução parcial.
- **Postos não contados:** reportados em cortes, mas excluídos pela fonte. Não adicionar ao total contabilizado.
- **Cortes quantificados:** parcela dos cortes com quantidade conhecida; desconhecido não é zero.
- **Mediana:** somente eventos de corte com quantidade conhecida.
- **Atribuição à IA:** empregador cita IA, IA entre vários fatores ou associação por outras fontes.
- **Evidências:** fontes primárias, jornalismo identificado ou evidência limitada; não são graus de causalidade.
- **Famílias ocupacionais:** um evento pode aparecer em várias; suas contagens não devem ser somadas.
- **Declarações sem corte:** fora da população de eventos de corte.

Os filtros de empresas alteram apenas os dois novos rankings e suas tabelas. Os cartões usam o registro completo.
O controle da evolução mensal altera apenas aquele gráfico; as seis comparações anteriores mantêm o snapshot completo.
`Atualizar` relê os indicadores materializados, sem baixar outra versão do dataset.
""")

st.html(f"""<footer class="rodape"><div><strong>FONTE / </strong>
<a href="https://ailayoffs.org" target="_blank" rel="noopener noreferrer">AI Layoffs Index</a>
· {snapshot} · metodologia v{escape(str(fonte["metodologia"]))}<br>
Análise independente, sem endosso do publicador. Associação não comprova causalidade.</div>
<a href="https://github.com/adrianobuilder/demissoes_ia/blob/main/raw/ai-layoffs-register.csv"
target="_blank" rel="noopener noreferrer">Registro e fontes dos eventos ↗</a></footer>""")
