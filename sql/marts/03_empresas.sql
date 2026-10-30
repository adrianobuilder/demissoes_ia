-- Grão: nome de empresa informado, apenas cortes; sem consolidação por semelhança.
SELECT empresa,
       count(*) AS eventos_corte,
       count(postos_contabilizados) AS eventos_quantificados,
       sum(postos_contabilizados) AS postos_contabilizados
FROM refined.eventos
WHERE tipo_evento = 'cut'
GROUP BY empresa
ORDER BY postos_contabilizados DESC NULLS LAST, empresa
