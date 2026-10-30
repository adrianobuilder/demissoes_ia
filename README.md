# Registro de demissões associadas à IA

Projeto acadêmico independente sobre eventos de cortes associados à IA. Python/uv e DuckDB fazem a carga em três camadas; cada indicador é definido em SQL. O roteiro e os contratos completos estão em [doc.md](doc.md).

## Fonte e licença

- [AI Layoffs Register no Kaggle](https://www.kaggle.com/datasets/ailayoffs/ai-layoffs-register-2023-2026-every-row-sourced), publicado pelo **AI Layoffs Index**.
- Snapshot: **23/10/2026**, metodologia **1.36**. Essa metodologia não é a versão numérica do Kaggle.
- [Licença recebida](fontes/LICENSE_dataset.txt) e [página canônica](https://ailayoffs.org/license): AI Layoffs Index and Register: Data License, com permissão para redistribuir o registro e produzir análises, mediante atribuição ao publicador e às fontes dos eventos. Não é uma licença Creative Commons.
- [README original](fontes/README_dataset.md), [proveniência e hash](fontes/proveniencia.json) e [perfil da cópia](fontes/perfil_fonte.json).

O CSV recebido acompanha `raw/` sem edição. Para citar um evento, preservar seu identificador e link de fonte. Esta análise não é uma leitura oficial do índice e não implica endosso do publicador. As URLs não concedem permissão para redistribuir os artigos de terceiros.

## Perguntas e modelo

Vamos estudar evolução mensal, empresas, atribuição à IA, execução, evidências, famílias ocupacionais e concentração dos postos contabilizados.

| Camada / tabela prevista | O que uma linha representa |
|---|---|
| `raw.eventos` | Registro exatamente como recebido no CSV, com campos textuais |
| `refined.eventos` | Evento tipado, identificado por `evento_id` |
| `refined.evento_familia` | Par único `evento_id` + `familia_ocupacional` |
| `marts.*` | Indicador no grão declarado no respectivo arquivo SQL |

As duas tabelas refined terão relação de um evento para várias famílias. O indicador de famílias usará JOIN por `evento_id`, contará eventos distintos e não somará postos depois da expansão.

## Estado da construção

- **A — fonte e pergunta:** cópia preservada, licença conferida e perfil registrado. Há 320 eventos e 498 pares evento–família, cobrindo os mesmos 320 IDs sem órfãos na derivação diagnóstica. Esses valores não são expectativas dos testes unitários.
- **B — ambiente:** Python 3.14.3, DuckDB 2.0.0, pandas 3.1.0, Streamlit 1.66.1 e Plotly 7.1.0 disponíveis. pytest-cov acrescentado; coleta em `test/`, cobertura total mínima de 60% e Ruff configurados.
- **C a G — pipeline, SQLs, apresentação e validação:** pendentes. Os contratos estão no guia; os comandos de reprodução serão incluídos à medida que os módulos forem verificados.

## Preparar o ambiente

Pré-requisitos: Git, uv e Python compatível com `requires-python` no `pyproject.toml`. O uv pode obter o interpretador necessário.

```powershell
git clone https://github.com/adrianobuilder/demissoes_ia.git
cd demissoes_ia
uv sync --locked
```

O nome da pasta clonada pode diferir de `demissao_ia`; os caminhos de produção serão baseados na localização dos módulos. Os arquivos de entrada estão versionados. `.gitattributes` preserva os bytes do CSV e dos documentos originais, inclusive no Windows.

## Limites de interpretação

Eventos de corte e declarações sem corte são populações diferentes. Postos contabilizados e postos reportados não contabilizados não serão somados. Ausência de quantidade não equivale a zero. Associação à IA não comprova causalidade; postos contabilizados também podem pertencer a anúncios ou execução parcial.

## Uso da IA: conferências e correções

Na preparação do guia, o total reportado exigiu revisão da população: todas as linhas somam 285.969, mas uma declaração sem corte contém 7.800. A conferência por tipo de evento determinou 278.169 para o indicador restrito aos cortes. O diagnóstico ficou registrado em `fontes/perfil_fonte.json`; os testes usarão exemplos inventados para verificar essa separação.

O desenho inicial usava uma CTE para famílias. O requisito adicional de duas tabelas relacionadas levou à tabela física `evento_familia`; essa é uma adaptação ao desafio, não uma segunda fonte independente.
