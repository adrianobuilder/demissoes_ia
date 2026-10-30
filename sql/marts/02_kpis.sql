-- Grão: snapshot inteiro, uma linha; ambas as CTEs agregadas têm uma linha.
-- Cortes e declarações são populações diferentes. Não somar os dois campos de postos.
-- Somas desconhecidas, mediana vazia e proporção sem denominador permanecem NULL.
WITH cortes AS (
    SELECT count(*) AS eventos_corte,
           count(DISTINCT empresa) AS empresas_com_cortes,
           sum(postos_contabilizados) AS postos_contabilizados,
           sum(postos_reportados_nao_contabilizados) AS postos_reportados_nao_contabilizados,
           round(100.0 * count(postos_contabilizados) / nullif(count(*), 0), 1)
               AS pct_cortes_quantificados,
           median(postos_contabilizados) AS mediana_postos_contabilizados
    FROM refined.eventos
    WHERE tipo_evento = 'cut'
), declaracoes AS (
    SELECT count(*) AS declaracoes_sem_corte
    FROM refined.eventos
    WHERE tipo_evento = 'workforce statement'
)
SELECT * FROM cortes CROSS JOIN declaracoes
