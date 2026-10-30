-- Grão: nível de evidência entre cortes; dimensão distinta da atribuição à IA.
SELECT coalesce(nivel_evidencia, 'Não informado') AS nivel_evidencia,
       count(*) AS eventos_corte,
       round(100.0 * count(*) / nullif(sum(count(*)) OVER (), 0), 1) AS pct_eventos
FROM refined.eventos
WHERE tipo_evento = 'cut'
GROUP BY 1
ORDER BY nivel_evidencia
