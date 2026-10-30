-- Pergunta: quais empresas têm mais eventos de corte em cada período e
-- em quantos desses eventos o empregador cita IA?
-- Grão: empresa + tipo de período (total/ano/mes) + início do período.
-- Cada evento cut aparece uma vez por nível; nunca somar níveis entre si.
-- Data do evento, obrigatória em refined, não data de execução.
-- Não exige quantidade de postos: desconhecido não elimina a empresa.
-- explicit é declaração do empregador; não prova causa exclusiva ou execução.
-- Rankings por eventos, com desempate alfabético para exibir exatamente top 5.
WITH cortes AS (
    SELECT empresa, data_evento, atribuicao_ia
    FROM refined.eventos
    WHERE tipo_evento = 'cut'
), recortes AS (
    SELECT 'total' AS tipo_periodo, NULL::DATE AS inicio_periodo, * FROM cortes
    UNION ALL
    SELECT 'ano', date_trunc('year', data_evento)::DATE, * FROM cortes
    WHERE data_evento IS NOT NULL
    UNION ALL
    SELECT 'mes', date_trunc('month', data_evento)::DATE, * FROM cortes
    WHERE data_evento IS NOT NULL
), resumo AS (
    SELECT tipo_periodo, inicio_periodo, empresa,
           count(*) AS eventos_corte,
           count(*) FILTER (WHERE atribuicao_ia = 'explicit') AS ia_empregador,
           count(*) FILTER (WHERE atribuicao_ia = 'mixed') AS ia_entre_fatores,
           count(*) FILTER (WHERE atribuicao_ia = 'blamed') AS ia_outras_fontes,
           count(*) FILTER (WHERE atribuicao_ia IS NULL
                            OR atribuicao_ia NOT IN ('explicit', 'mixed', 'blamed'))
               AS ia_nao_classificada,
           min(data_evento) AS primeiro_evento,
           max(data_evento) AS ultimo_evento
    FROM recortes
    GROUP BY tipo_periodo, inicio_periodo, empresa
)
SELECT *,
       sum(eventos_corte) OVER periodo AS eventos_periodo,
       sum(ia_empregador) OVER periodo AS ia_empregador_periodo,
       row_number() OVER (
           PARTITION BY tipo_periodo, inicio_periodo
           ORDER BY eventos_corte DESC, empresa
       ) AS posicao_eventos,
       row_number() OVER (
           PARTITION BY tipo_periodo, inicio_periodo
           ORDER BY ia_empregador DESC, empresa
       ) AS posicao_ia_empregador
FROM resumo
WINDOW periodo AS (PARTITION BY tipo_periodo, inicio_periodo)
ORDER BY tipo_periodo, inicio_periodo, posicao_eventos
