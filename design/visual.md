# Composição do dashboard — revisão 2

O pedido de revisão exige mudar a composição e os tipos de gráficos, seguindo o dashboard financeiro fornecido pelo usuário. A primeira modernização, registrada nos commits `f3fda44` e `28bef30`, mudou principalmente cores e cartões e foi considerada insuficiente pelo usuário. Esta revisão substitui aquela composição.

## Estrutura adotada

Cabeçalho azul-marinho compacto, marca, navegação por âncoras e controles de aparência/recarga. Título e snapshot numa faixa curta. Superfícies retangulares, cantos de 4–5 px, bordas discretas, títulos em caixa alta e pouco espaço entre os blocos, como na referência. Sem o grande bloco de apresentação anterior.

```text
MARCA / NAVEGAÇÃO                              CLARO · ESCURO / ATUALIZAR
Título do registro                                      Snapshot da fonte
4 indicadores principais: cortes / empresas / postos contados / não contados
3 indicadores complementares: cobertura / mediana / declarações

01 PANORAMA DOS CORTES
┌──────────────────────────────────┬─────────────────────┐
│ Barras mensais + filtro           │ Rosca: atribuição   │
└──────────────────────────────────┴─────────────────────┘
02 DISTRIBUIÇÃO E EVIDÊNCIAS
┌───────────────────┬───────────────────┬────────────────┐
│ Barras: empresas  │ Colunas: execução │ Pizza: fontes  │
└───────────────────┴───────────────────┴────────────────┘
03 OCUPAÇÕES E CONCENTRAÇÃO
┌────────────────────────────────┬───────────────────────┐
│ Barras: 12 famílias             │ Curva de concentração │
│                                ├───────────────────────┤
│                                │ Tabela: 5 empresas    │
└────────────────────────────────┴───────────────────────┘
Metodologia / atribuição e fontes
```

## Figuras compartilhadas

| ID | Função em `painel.py` | Forma / critério |
|---|---|---|
| g01 | `cortes_mensais` | Colunas para postos mensais; ausente permanece ausente, eixo em zero; até quatro datas |
| g02 | `eventos_por_atribuicao` | Rosca de três categorias exclusivas, percentuais e legenda |
| g03 | `postos_por_empresa` | Dez maiores totais conhecidos, barras horizontais e valores diretos |
| g04 | `eventos_por_execucao` | Colunas para as cinco situações; “Desconh.” no eixo, nome completo no hover |
| g05 | `eventos_por_evidencia` | Pizza com Tier 1/2/3, percentuais e legenda |
| g06 | `eventos_por_familia` | Barras horizontais das doze famílias; contagens sobrepostas, nunca pizza |
| g07 | `concentracao_empresas` | Curva com área discreta e referência tracejada de 80% |

`tabela_empresas` ordena e formata as cinco primeiras linhas do mart de empresas. Não soma, não junta tabelas nem cria medidas. A tabela escapa o texto da fonte antes de inseri-lo no HTML.

Os SQLs, populações e sete valores dos cartões permanecem iguais. As pizzas usam contagens de eventos para as áreas e percentuais já calculados nos marts para os textos; arredondamentos podem resultar em 100,1%. Cada classificação forma uma partição dos cortes. Famílias se sobrepõem e não podem ser partes de um todo. O hover mantém contagem, percentual e classificação de origem. Nenhum mapa, preço de ação, comparação de crescimento ou gráfico financeiro sem dado correspondente foi acrescentado.

## Temas e responsividade

- Claro por padrão e escuro por seletor, persistentes na sessão após filtro e recarga.
- Página, gráficos, legendas, controles e tabela seguem a paleta. Tons fixos por categoria nas pizzas, com textos claros ou escuros conforme o contraste; não depender somente da cor.
- Quatro cartões principais e três medidas complementares numa faixa compacta. Abaixo de 950 px, principais em duas colunas e gráficos empilhados. Abaixo de 650 px, cabeçalho se reorganiza e ícones decorativos dos cartões são ocultados para acomodar os rótulos.
- Filtro só no mensal; cartões e seis comparações usam o snapshot completo. `Atualizar` relê os marts, sem baixar nova fonte.
- Manter Streamlit/Plotly e CSS local, sem novas dependências. `theme=None` respeita as cores das figuras.
- HTML estático usa as mesmas quatro faixas, figuras e tabela no tema claro, com IDs fixos, CDN único, geração datada e tamanho inferior a 200 KB.

## Aceite e evidências

Conferir sete valores e sete figuras; barras, rosca e pizza renderizadas; percentuais coerentes com os marts; nenhuma soma de famílias; ausência preservada no mensal; filtro e recarga sem mudar o tema; tabela sem agregações. Validar no Chrome em 1310 × 581 e 390 × 844, claro e escuro, com títulos, legendas e números legíveis. Capturas reais do cabeçalho: [claro](painel-claro.jpg), [escuro](painel-escuro.jpg). Capturas dos gráficos: [claro](graficos-claro.jpg), [escuro](graficos-escuro.jpg), [panorama](panorama-claro.jpg).

A reprodução em clone limpo da etapa G e a primeira validação visual permanecem históricas em `fontes/validacao_entrega.json` e `fontes/validacao_visual.json`. Esta revisão tem seu próprio registro em `fontes/validacao_design_v2.json`. A abertura manual do HTML local continua pendente; o bloqueio do protocolo `file://` pela ferramenta não foi contornado.
