"""Gerar relatorio.html na raiz, reutilizando exclusivamente painel.py.

Spec: sete cartões HTML, nove figuras nas mesmas cinco faixas do app; período
mensal completo, sem filtro. Um só arquivo com CSS embutido, Plotly CDN somente
no primeiro gráfico, div_id g01..g09 fixos. Menos de 200 KB. Com dados/ambiente
iguais, só varia o rodapé 'Dados de DD/MM/AAAA HH:MM', em America/Sao_Paulo.
Snapshot da fonte é identificado separadamente. stdout UTF-8 com caminho e KB.
Não importar Streamlit nem app.py; não criar outros gráficos ou indicadores.
"""

from datetime import date, datetime
from html import escape
from zoneinfo import ZoneInfo

import duckdb

import painel
from pipeline import db

SAIDA = db.RAIZ / "relatorio.html"
FUSO = ZoneInfo("America/Sao_Paulo")
LIMITE_BYTES = 200 * 1024
CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #f5f7fa; color: #172033; font-family: Arial, sans-serif; }
main { max-width: 1640px; margin: auto; padding: 32px 24px; }
h1 { font-size: 30px; margin: 0 0 12px; line-height: 1.25; }
p { line-height: 1.5; }
a { color: #1d4ed8; }
.contexto, footer { color: #475569; font-size: 13px; }
.cartoes { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 12px; margin: 20px 0 16px; }
.cartao { grid-column: span 3; background: white; padding: 14px; border: 1px solid #dce3ec; border-top: 3px solid #235c95; border-radius: 4px; }
.cartao:nth-child(n+5) { grid-column: span 4; border-top-width: 1px; }
.cartao h2 { margin: 0; font-size: 13px; line-height: 1.4; font-weight: 600; }
.valor { font-size: 28px; margin: 10px 0; font-variant-numeric: tabular-nums; }
.definicao { margin: 0; color: #475569; font-size: 12px; }
.grade { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.panorama { grid-template-columns: 2fr 1fr; }
.rankings { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.event-table { overflow: auto; max-height: 420px; }
.event-table table { min-width: 780px; }
.ocupacoes { grid-template-columns: 1.25fr 1fr; align-items: start; }
.coluna { display: grid; gap: 14px; min-width: 0; }
.section-title { font-size: 12px; letter-spacing: .7px; border-bottom: 2px solid #dce3ec; padding-bottom: 8px; margin-top: 24px; }
.company-table { background: white; border: 1px solid #dce3ec; border-radius: 4px; padding: 14px; }
.company-table h3 { font-size: 11px; margin: 0 0 10px; }
.company-table h3 span { float: right; color: #52657e; font-size: 10px; font-weight: 400; }
.company-table table { width: 100%; border-collapse: collapse; font-size: 11px; }
.company-table th, .company-table td { text-align: right; padding: 7px 8px; border-bottom: 1px solid #e7edf5; }
.company-table th:first-child, .company-table td:first-child { text-align: left; }
.company-table th, .company-table tr:nth-child(even) { background: #f7faff; }
.grafico { min-width: 0; overflow: hidden; background: white; border: 1px solid #dce3ec; border-radius: 8px; }
.faixa { margin-top: 20px; }
footer { margin-top: 28px; border-top: 1px solid #dce3ec; padding-top: 16px; }
@media (max-width: 1000px) { .grade { grid-template-columns: 1fr; } }
@media (max-width: 650px) {
  main { padding: 24px 12px; }
  h1 { font-size: 25px; }
  .cartoes { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .cartao, .cartao:nth-child(n+5) { grid-column: span 1; }
  .cartao:last-child { grid-column: span 2; }
  .cartao { padding: 12px; }
}
"""


def montar_html(dados, gerado_em: datetime, proveniencia: dict) -> str:
    cartoes = []
    for cartao in painel.cartoes(dados):
        cartoes.append(
            '<article class="cartao">'
            f"<h2>{escape(cartao['titulo'])}</h2>"
            f'<p class="valor">{escape(cartao["valor"])}</p>'
            f'<p class="definicao">{escape(cartao["ajuda"])}</p></article>'
        )
    graficos = []
    empresas = painel.selecionar_periodo(dados["empresas_periodo"])
    figuras = painel.figuras_empresas(empresas) + painel.figuras(dados)
    for indice, figura in enumerate(figuras, start=1):
        fragmento = figura.to_html(
            full_html=False,
            include_plotlyjs="cdn" if indice == 1 else False,
            div_id=f"g{indice:02}",
            config={"responsive": True, "displaylogo": False},
        )
        graficos.append(f'<article class="grafico">{fragmento}</article>')
    snapshot = date.fromisoformat(proveniencia["snapshot"]).strftime("%d/%m/%Y")
    metodologia = escape(str(proveniencia["metodologia"]))
    horario = gerado_em.astimezone(FUSO).strftime("%d/%m/%Y %H:%M")
    return f"""<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Registro de demissões associadas à IA</title><style>{CSS}</style></head>
<body><main>
<header><h1>Registro de demissões associadas à IA</h1>
<p class="contexto">Fonte: <a href="https://ailayoffs.org">AI Layoffs Index</a> ·
Snapshot da fonte: {snapshot} · metodologia v{metodologia}.</p></header>
<section id="faixa01" class="cartoes" aria-label="Indicadores do snapshot">{"".join(cartoes)}</section>
<p class="contexto">Cartões e comparações representam o snapshot inteiro. O gráfico mensal mostra
o período completo disponível. Postos contabilizados podem estar anunciados ou parcialmente
executados. Associação à IA não comprova causalidade; quantidade desconhecida não significa zero.</p>
<h2 class="section-title">01 / QUAIS EMPRESAS MAIS REGISTRARAM CORTES?</h2>
<section id="faixa02" class="faixa" aria-label="Empresas por eventos e IA">
<p class="contexto">Um evento é um registro de corte, não uma pessoa demitida.
O ranking com IA conta somente eventos em que o empregador citou IA; isso não prova causa exclusiva.
Período: todo o registro. Até 5 empresas por gráfico, com desempate por nome.</p>
<div class="grade rankings">{"".join(graficos[:2])}</div>{painel.tabela_eventos_html(empresas)}</section>
<h2 class="section-title">02 / PANORAMA DOS CORTES</h2>
<section id="faixa03" class="faixa grade panorama" aria-label="Evolução mensal e atribuição">{"".join(graficos[2:4])}</section>
<h2 class="section-title">03 / DISTRIBUIÇÃO E EVIDÊNCIAS</h2>
<section id="faixa04" class="faixa grade" aria-label="Postos, execução e evidências">{"".join(graficos[4:7])}</section>
<h2 class="section-title">04 / OCUPAÇÕES E CONCENTRAÇÃO</h2>
<section id="faixa05" class="faixa grade ocupacoes" aria-label="Famílias e concentração">{graficos[7]}
<div class="coluna">{graficos[8]}{painel.tabela_empresas(dados["empresas"])}</div></section>
<p class="contexto">Um evento pode pertencer a várias famílias ocupacionais. Não somar as contagens
por família nem adicionar postos reportados não contabilizados aos contabilizados.</p>
<footer><p>Dados de {horario}</p>
<p>Gerado a partir do snapshot identificado no cabeçalho; este arquivo não consulta o banco.
Os gráficos precisam de internet para carregar Plotly pelo CDN.</p>
<p>Fontes de cada evento no
<a href="https://github.com/adrianobuilder/demissoes_ia/blob/main/raw/ai-layoffs-register.csv">CSV do registro</a>.
Esta análise não é uma leitura oficial do índice e não implica endosso do publicador.</p></footer>
</main></body></html>
"""


def main():
    db.configurar_stdout()
    try:
        html = montar_html(painel.ler(), datetime.now(FUSO), painel.proveniencia())
        tamanho = len(html.encode("utf-8"))
        if tamanho >= LIMITE_BYTES:
            raise ValueError("Relatório deve ter menos de 200 KB; arquivo anterior preservado")
        SAIDA.write_text(html, encoding="utf-8", newline="\n")
    except (OSError, ValueError, KeyError, duckdb.Error) as exc:
        raise SystemExit(f"Erro no relatório: {exc}") from exc
    print(f"Relatório: {SAIDA.resolve()} ({painel.numero(tamanho / 1024, 1)} KB)")


if __name__ == "__main__":
    main()
