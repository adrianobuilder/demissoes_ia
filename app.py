"""Painel de composição financeira; spec em painel.py e design/visual.md.

Sete cartões e figuras compartilhadas, tabela do mart de empresas e quatro
faixas. Temas claro/escuro, cache sem conexão aberta e filtro só mensal.
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


with st.container(key="topbar"):
    marca, aparencia, recarga = st.columns([4.8, 1.6, 1.1], vertical_alignment="center")
    with marca:
        st.html("""<div class="masthead"><span class="brand-mark">IA</span>
<div class="brand-name">TRABALHO &amp; TECNOLOGIA<small>DATA INTELLIGENCE / REGISTRO DE DEMISSÕES</small></div>
<nav aria-label="Seções do painel"><a href="#evolucao">PANORAMA</a>
<a href="#distribuicao">DISTRIBUIÇÃO</a><a href="#ocupacoes">OCUPAÇÕES</a></nav></div>""")
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

divisao("01", "PANORAMA DOS CORTES", "Evolução e composição do registro", "evolucao")
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
    "02",
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
    "03",
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

Cartões e seis gráficos de comparação usam o snapshot completo. Só a evolução mensal responde ao filtro.
`Atualizar` relê os indicadores materializados, sem baixar outra versão do dataset.
""")

st.html(f"""<footer class="rodape"><div><strong>FONTE / </strong>
<a href="https://ailayoffs.org" target="_blank" rel="noopener noreferrer">AI Layoffs Index</a>
· {snapshot} · metodologia v{escape(str(fonte["metodologia"]))}<br>
Análise independente, sem endosso do publicador. Associação não comprova causalidade.</div>
<a href="https://github.com/adrianobuilder/demissoes_ia/blob/main/raw/ai-layoffs-register.csv"
target="_blank" rel="noopener noreferrer">Registro e fontes dos eventos ↗</a></footer>""")
