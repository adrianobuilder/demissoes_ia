# Modernização visual

Referências: os dois dashboards fornecidos pelo usuário, com cabeçalho azul-marinho, cartões de indicadores, grades alinhadas e hierarquia clara entre números, gráficos e contexto.

## Decisões

- Preservar as quatro faixas lógicas, os sete cartões e as sete figuras existentes. Nenhum indicador novo ou comparação de crescimento será inventado.
- Manter Streamlit e Plotly. Tema claro como padrão; seletor visível permite tema escuro na mesma sessão, inclusive após filtros e recarga.
- Usar superfícies claras/azul-marinho, bordas discretas, ícones, valores em destaque e espaços consistentes. Contraste do texto, dos controles e dos gráficos acompanha o tema.
- Exibir títulos de negócio e traduzir rótulos das classificações. A ligação com os SQLs permanece no README, em vez de ocupar o título de cada gráfico.
- Diminuir alturas dos gráficos e reservar mais espaço para as doze famílias. Manter valores diretos, barras começando em zero e lacunas de quantidade desconhecida.
- Em telas menores, reorganizar os cartões e empilhar os gráficos. Usar apenas CSS local e recursos já instalados, sem imagens decorativas ou fontes externas.
- O relatório HTML reutiliza as mesmas funções no tema claro. Sua geração e seu limite de tamanho continuam válidos.

## Verificação

Conferir os dois temas em tela normal e estreita; sete valores, sete gráficos, seleção mensal e recarga. Comparar coordenadas dos gráficos entre temas e executar a suíte existente. Registrar as verificações efetivamente realizadas no README e enviar cada implementação ao GitHub.
