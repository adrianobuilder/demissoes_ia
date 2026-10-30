-- Grão: situação de execução entre cortes. Incluir todas as situações declaradas.
SELECT coalesce(situacao_execucao, 'Não informado') AS situacao_execucao,
       count(*) AS eventos_corte,
       round(100.0 * count(*) / nullif(sum(count(*)) OVER (), 0), 1) AS pct_eventos
FROM refined.eventos
WHERE tipo_evento = 'cut'
GROUP BY 1
ORDER BY eventos_corte DESC, situacao_execucao
