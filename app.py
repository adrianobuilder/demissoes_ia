"""Dashboard Streamlit; a spec de apresentação está em painel.py e design/visual.md.

Sete cartões e sete figuras em quatro faixas, nos temas claro e escuro. O tema
persiste na sessão e altera só a aparência. Cachear dados, sem conexão aberta.
Período padrão completo; filtro apenas no mensal. Recarga limpa o cache; falha de
leitura mostra orientação e interrompe. Executar: uv run streamlit run app.py.
"""

from datetime import date
from html import escape

import duckdb
import pandas as pd
import streamlit as st

import painel

st.set_page_config(page_title="Demissões associadas à IA", page_icon="📊", layout="wide")


@st.cache_data(show_spinner=False)
def carregar():
    return painel.ler(), painel.proveniencia()


def secao(titulo, descricao, detalhe=""):
    st.html(
        '<div class="section-heading"><div>'
        f"<h2>{escape(titulo)}</h2><p>{escape(descricao)}</p></div>"
        f'<span class="section-hint">{escape(detalhe)}</span></div>'
    )


with st.container(key="barra_superior"):
    marca, aparencia, recarga = st.columns([3.5, 1.5, 1.2], vertical_alignment="center")
    with marca:
        st.html(
            '<div class="app-brand"><span class="marca" aria-hidden="true">IA</span>'
            "<div><strong>TRABALHO &amp; TECNOLOGIA</strong>"
            "<small>Registro de eventos e evidências</small></div></div>"
        )
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
        if st.button("Atualizar dados", icon=":material/refresh:", width="stretch"):
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

st.html(f"""
<div class="hero">
  <div>
    <div class="eyebrow">PANORAMA DOS REGISTROS</div>
    <h1>Demissões associadas à IA</h1>
    <p>Explore os eventos de corte, as empresas envolvidas e as evidências disponíveis.
    Uma visão organizada do registro, com contexto para interpretar cada número.</p>
  </div>
  <div class="hero-meta">
    <span>Snapshot da fonte</span><strong>{snapshot}</strong>
    <span class="selo">Metodologia v{escape(str(fonte["metodologia"]))}</span>
  </div>
</div>
""")

secao(
    "Visão geral",
    "Os principais números do registro",
    "Todos os indicadores usam o snapshot inteiro",
)
icones = (
    ":material/event_note:",
    ":material/domain:",
    ":material/badge:",
    ":material/filter_alt_off:",
    ":material/fact_check:",
    ":material/equalizer:",
    ":material/chat_bubble_outline:",
)
with st.container(key="cartoes"):
    for coluna, cartao, icone in zip(st.columns(7), cartoes, icones, strict=True):
        coluna.metric(
            cartao["titulo"], cartao["valor"], help=cartao["ajuda"], icon=icone, border=True
        )

st.html("""
<div class="aviso" role="note"><span class="simbolo" aria-hidden="true">ⓘ</span><div>
<b>Contexto importa.</b> Associação à IA não comprova causalidade. Postos contabilizados podem
estar anunciados ou parcialmente executados. Quantidade desconhecida não significa zero.
</div></div>
""")

secao(
    "Evolução dos registros",
    "Acompanhe os postos contabilizados ao longo do tempo",
    "O filtro abaixo altera somente este gráfico",
)
mensal = dados["cortes_mensais"]
meses = [pd.Timestamp(mes).date() for mes in mensal["mes"].sort_values()]
if not meses:
    st.error("O mart mensal está vazio. Reconstrua os indicadores.")
    st.stop()
with st.container(key="evolucao"):
    with st.container(key="filtro_periodo"):
        if len(meses) > 1:
            inicio, fim = st.select_slider(
                "Período do gráfico mensal",
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
    st.plotly_chart(
        figuras[0], width="stretch", key="g01", theme=None, config={"displaylogo": False}
    )

with st.container(key="graficos"):
    secao(
        "Distribuição dos cortes",
        "Empresas, atribuição à IA e situação de execução",
        "Snapshot completo",
    )
    for coluna, indice in zip(st.columns(3), (1, 2, 3), strict=True):
        with coluna, st.container(key=f"quadro_{indice}"):
            st.plotly_chart(
                figuras[indice],
                width="stretch",
                key=f"g{indice + 1:02}",
                theme=None,
                config={"displaylogo": False},
            )
    secao(
        "Evidências e concentração",
        "Os tipos de trabalho, as fontes e a distribuição dos postos",
        "Famílias ocupacionais se sobrepõem",
    )
    for coluna, indice in zip(st.columns(3), (4, 5, 6), strict=True):
        with coluna, st.container(key=f"quadro_{indice}"):
            st.plotly_chart(
                figuras[indice],
                width="stretch",
                key=f"g{indice + 1:02}",
                theme=None,
                config={"displaylogo": False},
            )

with st.expander("Como ler este painel", icon=":material/info:"):
    st.markdown("""
- **Postos contabilizados:** quantidades aceitas pela metodologia da fonte, incluindo anúncios e execução parcial.
- **Postos não contados:** quantidades reportadas em cortes, mas excluídas pela fonte. Não adicionar ao total contabilizado.
- **Cortes quantificados:** parcela dos eventos de corte que tem quantidade contabilizada conhecida.
- **Atribuição à IA:** distingue a declaração do empregador, a IA entre vários fatores e a associação por outras fontes.
- **Níveis de evidência:** fontes primárias, jornalismo identificado ou evidência limitada. Não equivalem a graus de causalidade.
- **Famílias ocupacionais:** um evento pode aparecer em várias. Suas contagens não devem ser somadas.
- **Declarações sem corte:** não fazem parte da população de eventos de corte.

Os cartões e seis gráficos de comparação usam o snapshot completo. Apenas a evolução mensal responde ao filtro.
`Atualizar dados` relê os indicadores materializados; não baixa uma nova versão do dataset.
""")

st.html(f"""
<div class="rodape">
  <div>Fonte: <a href="https://ailayoffs.org" target="_blank" rel="noopener noreferrer"><strong>AI Layoffs Index</strong></a>
  · {snapshot} · metodologia v{escape(str(fonte["metodologia"]))}<br>
  Análise independente. Não representa a leitura oficial do índice nem endosso do publicador.</div>
  <div><a href="https://github.com/adrianobuilder/demissoes_ia/blob/main/raw/ai-layoffs-register.csv"
  target="_blank" rel="noopener noreferrer">Consultar o registro e as fontes dos eventos ↗</a></div>
</div>
""")
