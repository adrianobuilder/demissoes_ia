# Modernização visual

Referências: os dois dashboards fornecidos pelo usuário, com cabeçalho azul-marinho, cartões de indicadores, grades alinhadas e hierarquia clara entre números, gráficos e contexto.

## Decisões

- Preservar as quatro faixas lógicas, os sete cartões e as sete figuras existentes. Nenhum indicador novo ou comparação de crescimento será inventado.
- Manter Streamlit e Plotly. Tema claro como padrão; seletor visível permite tema escuro na mesma sessão, inclusive após filtros e recarga.
- Usar superfícies claras/azul-marinho, bordas discretas, ícones, valores em destaque e espaços consistentes. Contraste do texto, dos controles e dos gráficos acompanha o tema.
- Exibir títulos de negócio e traduzir rótulos das classificações. A ligação com os SQLs permanece no README, em vez de ocupar o título de cada gráfico.
- Diminuir alturas dos gráficos e reservar mais espaço para as doze famílias. Manter valores diretos, barras começando em zero e lacunas de quantidade desconhecida.
- Em telas menores, reorganizar os cartões e empilhar os gráficos. Usar apenas CSS local e recursos já instalados, sem imagens decorativas ou fontes externas.
- Cartões em quatro e três no desktop; duas colunas abaixo de 1050 px, último cartão expandido. Abaixo de 650 px, ocultar ícones decorativos dos cartões para dar espaço aos rótulos. Até quatro datas no eixo mensal; nenhum ponto é removido.
- O relatório HTML reutiliza as mesmas funções no tema claro. Sua geração e seu limite de tamanho continuam válidos.

## Verificação

Conferir os dois temas em tela normal e estreita; sete valores, sete gráficos, seleção mensal e recarga. Comparar coordenadas dos gráficos entre temas e executar a suíte existente. Registrar as verificações efetivamente realizadas no README e enviar cada implementação ao GitHub.

Concluída em 30/10/2026: 44 testes, 97,97% de cobertura, Ruff e AppTest aprovados. Chrome em 1310 × 581 e 390 × 844; contraste e gráficos nos dois temas, rótulos sem truncamento e datas mensais sem sobreposição no celular. Capturas reais: [claro](painel-claro.jpg) e [escuro](painel-escuro.jpg). A reprodução em clone limpo da etapa G permanece como registro histórico; não foi repetida nesta revisão visual.
