# Composição do dashboard — revisão 3

O pedido de revisão exige mudar a composição e os tipos de gráficos, seguindo o dashboard financeiro fornecido pelo usuário. A primeira modernização, registrada nos commits `f3fda44` e `28bef30`, mudou principalmente cores e cartões e foi considerada insuficiente pelo usuário. Esta revisão substitui aquela composição.

A revisão 3 atende à dificuldade de leitura apontada pelo usuário: antes do panorama, apresenta quantos eventos cada empresa registra por período e em quantos o empregador citou IA. A composição financeira da revisão 2 permanece, com essa seção adicional e títulos que distinguem eventos de postos.

## Estrutura adotada

Cabeçalho azul-marinho compacto, marca, navegação por âncoras e controles de aparência/recarga. Título e snapshot numa faixa curta. Superfícies retangulares, cantos de 4–5 px, bordas discretas, títulos em caixa alta e pouco espaço entre os blocos, como na referência. Sem o grande bloco de apresentação anterior.

```text
MARCA / NAVEGAÇÃO                              CLARO · ESCURO / ATUALIZAR
Título do registro                                      Snapshot da fonte
4 indicadores principais: cortes / empresas / postos contados / não contados
3 indicadores complementares: cobertura / mediana / declarações

01 EMPRESAS POR PERÍODO
Ano / mês / empresa para consultar
┌───────────────────────────┬────────────────────────────┐
│ Top 5 por eventos         │ Top 5: empregador citou IA  │
└───────────────────────────┴────────────────────────────┘
Tabelas: resumo por empresa / mês a mês por empresa
02 PANORAMA DOS CORTES
┌──────────────────────────────────┬─────────────────────┐
│ Barras mensais + filtro           │ Rosca: atribuição   │
└──────────────────────────────────┴─────────────────────┘
03 DISTRIBUIÇÃO E EVIDÊNCIAS
┌───────────────────┬───────────────────┬────────────────┐
│ Barras: empresas  │ Colunas: execução │ Pizza: fontes  │
└───────────────────┴───────────────────┴────────────────┘
04 OCUPAÇÕES E CONCENTRAÇÃO
┌────────────────────────────────┬───────────────────────┐
│ Barras: 12 famílias             │ Curva de concentração │
│                                ├───────────────────────┤
│                                │ Tabela: 5 empresas    │
└────────────────────────────────┴───────────────────────┘
Metodologia / atribuição e fontes
```

## Figuras compartilhadas

| ID no HTML | Função em `painel.py` | Forma / critério |
|---|---|---|
| g01 | `ranking_eventos_empresa` | Até cinco empresas por quantidade de eventos, sem exigir postos conhecidos |
| g02 | `ranking_ia_empregador` | Até cinco empresas por eventos `explicit`, excluindo zeros |
| g03 | `cortes_mensais` | Colunas para postos mensais; ausente permanece ausente; até quatro datas |
| g04 | `eventos_por_atribuicao` | Rosca de categorias exclusivas, percentuais e legenda |
| g05 | `postos_por_empresa` | Dez maiores totais conhecidos, barras horizontais; rótulo explícito de postos |
| g06 | `eventos_por_execucao` | Colunas de situações; “Desconh.” no eixo, completo no hover |
| g07 | `eventos_por_evidencia` | Pizza com Tier 1/2/3, percentuais e legenda |
| g08 | `eventos_por_familia` | Barras das doze famílias; contagens sobrepostas, nunca pizza |
| g09 | `concentracao_empresas` | Curva com área discreta e referência de 80% |

`tabela_empresas` ordena e formata as cinco primeiras linhas do mart de empresas. Não soma, não junta tabelas nem cria medidas. A tabela escapa o texto da fonte antes de inseri-lo no HTML.

`09_empresas_periodo.sql` calcula contagens por empresa nos níveis total/ano/mês, atribuições e posições. A tela só seleciona um nível; nunca soma níveis. Rankings respeitam o ano/mês selecionado e desempate alfabético. A consulta de empresa filtra apenas as tabelas de resumo e meses com eventos. Os cartões do topo e comparações anteriores mantêm o registro completo. O mês depende de selecionar um ano; período sem eventos mostra mensagem clara. Um evento é um registro de corte, não uma pessoa. A categoria `explicit` indica declaração do empregador, sem comprovar causa exclusiva. Totais de postos continuam separados e não recebem o título genérico de ranking de cortes.

Os SQLs, populações e sete valores dos cartões permanecem iguais. As pizzas usam contagens de eventos para as áreas e percentuais já calculados nos marts para os textos; arredondamentos podem resultar em 100,1%. Cada classificação forma uma partição dos cortes. Famílias se sobrepõem e não podem ser partes de um todo. O hover mantém contagem, percentual e classificação de origem. Nenhum mapa, preço de ação, comparação de crescimento ou gráfico financeiro sem dado correspondente foi acrescentado.

## Temas e responsividade

- Claro por padrão e escuro por seletor, persistentes na sessão após filtro e recarga.
- Página, gráficos, legendas, controles e tabela seguem a paleta. Tons fixos por categoria nas pizzas, com textos claros ou escuros conforme o contraste; não depender somente da cor.
- Quatro cartões principais e três medidas complementares numa faixa compacta. Abaixo de 950 px, principais em duas colunas e gráficos empilhados. Abaixo de 650 px, cabeçalho se reorganiza e ícones decorativos dos cartões são ocultados para acomodar os rótulos.
- Filtro só no mensal; cartões e seis comparações usam o snapshot completo. `Atualizar` relê os marts, sem baixar nova fonte.
- Manter Streamlit/Plotly e CSS local, sem novas dependências. `theme=None` respeita as cores das figuras.
- HTML estático usa cinco faixas e nove figuras no tema claro, rankings do registro completo e tabela, com IDs fixos, CDN único, geração datada e tamanho inferior a 200 KB.

## Aceite e evidências

Conferir sete valores, nove figuras, ano/mês/empresa, consulta mensal, período vazio e manutenção dos escopos/temas. Os 52 testes passaram; cobertura de 97,85%, Ruff e AppTest aprovados. Chrome em 1310 × 581 e 390 × 844, claro/escuro; seletores com contraste e rankings empilhados. BenchSci/2025 mostrou um evento em agosto com `explicit`. Capturas da nova seção: [claro](empresas-claro.jpg), [escuro](empresas-escuro.jpg). Os demais gráficos preservam as formas da revisão 2.

A reprodução em clone limpo da etapa G e as revisões visuais anteriores permanecem históricas em `fontes/validacao_entrega.json`, `fontes/validacao_visual.json` e `fontes/validacao_design_v2.json`. A revisão 3 usa `fontes/validacao_empresas_periodo.json`. A abertura manual do HTML local continua pendente; o bloqueio de `file://` pela ferramenta não foi contornado.
