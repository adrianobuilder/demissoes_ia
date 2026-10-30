-- Grão: atribuição entre cortes. Percentual de eventos, não de postos.
-- mixed não é causa exclusiva; blamed não é confirmação pelo empregador.
SELECT coalesce(atribuicao_ia, 'Não informado') AS atribuicao_ia,
       count(*) AS eventos_corte,
       round(100.0 * count(*) / nullif(sum(count(*)) OVER (), 0), 1) AS pct_eventos
FROM refined.eventos
WHERE tipo_evento = 'cut'
GROUP BY 1
ORDER BY eventos_corte DESC, atribuicao_ia
