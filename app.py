"""Dashboard Streamlit; a spec de apresentação está na docstring de painel.py.

Ler só marts pela biblioteca compartilhada. Cachear dados, sem conexão aberta.
Sete cartões e sete figuras em quatro faixas. Período padrão completo e filtro
apenas no mensal. Recarga limpa o cache; falha de leitura mostra erro e interrompe.
Executar: uv run streamlit run app.py.
"""

from datetime import date

import duckdb
import pandas as pd
import streamlit as st

import painel

st.set_page_config(page_title="Registro de demissões associadas à IA", layout="wide")
st.html("""
<style>
@media (max-width: 1100px) {
  .st-key-cartoes [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
  .st-key-cartoes [data-testid="stColumn"] { flex: 1 1 150px !important; min-width: 150px !important; }
  .st-key-graficos [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
  .st-key-graficos [data-testid="stColumn"] { flex: 1 1 100% !important; min-width: 0 !important; }
}
</style>
""")


@st.cache_data(show_spinner=False)
def carregar():
    return painel.ler(), painel.proveniencia()


cabecalho, recarga = st.columns([4, 1.5])
with cabecalho:
    st.title("Registro de demissões associadas à IA")
with recarga:
    if st.button("Recarregar dados", width="stretch"):
        carregar.clear()

try:
    dados, fonte = carregar()
    cartoes = painel.cartoes(dados)
except (OSError, ValueError, duckdb.Error) as exc:
    st.error(
        f"Não foi possível ler os indicadores: {exc}. Execute uv run python -m pipeline.marts."
    )
    st.stop()

snapshot = date.fromisoformat(fonte["snapshot"]).strftime("%d/%m/%Y")
st.caption(
    f"Fonte: [AI Layoffs Index](https://ailayoffs.org) · Snapshot: {snapshot} · "
    f"Metodologia v{fonte['metodologia']}. Associação à IA não comprova causalidade."
)
with st.container(key="cartoes"):
    for coluna, cartao in zip(st.columns(7), cartoes, strict=True):
        coluna.metric(cartao["titulo"], cartao["valor"], help=cartao["ajuda"])

st.caption(
    "Cartões e seis gráficos de comparação representam o snapshot inteiro. "
    "O filtro abaixo altera somente o gráfico mensal. Postos contabilizados podem estar "
    "anunciados ou parcialmente executados; valores ausentes não significam zero."
)

mensal = dados["cortes_mensais"]
meses = [pd.Timestamp(mes).date() for mes in mensal["mes"].sort_values()]
if not meses:
    st.error("O mart mensal está vazio. Reconstrua os indicadores.")
    st.stop()
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
recorte = mensal.loc[(mensal["mes"] >= pd.Timestamp(inicio)) & (mensal["mes"] <= pd.Timestamp(fim))]
figuras = painel.figuras({**dados, "cortes_mensais": recorte})
st.plotly_chart(figuras[0], width="stretch", key="g01")
with st.container(key="graficos"):
    for indices in ((1, 2, 3), (4, 5, 6)):
        for coluna, indice in zip(st.columns(3), indices, strict=True):
            coluna.plotly_chart(figuras[indice], width="stretch", key=f"g{indice + 1:02}")

st.caption(
    "Famílias ocupacionais se sobrepõem: suas contagens não devem ser somadas. "
    "Os links das fontes de cada evento estão no CSV do "
    "[repositório](https://github.com/adrianobuilder/demissoes_ia/blob/main/raw/ai-layoffs-register.csv). "
    "Esta análise não é uma leitura oficial do índice e não implica endosso do publicador."
)
