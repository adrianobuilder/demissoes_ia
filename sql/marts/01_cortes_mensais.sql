-- Pergunta: como evoluem os cortes e os postos contabilizados por mês?
-- Grão: mês entre o primeiro e o último corte. A data é a do evento.
-- Contagens ausentes são zero; postos sem quantidade conhecida permanecem NULL.
WITH cortes AS (
    SELECT * FROM refined.eventos WHERE tipo_evento = 'cut'
), limites AS (
    SELECT date_trunc('month', min(data_evento))::DATE AS inicio,
           date_trunc('month', max(data_evento))::DATE AS fim
    FROM cortes
), calendario AS (
    SELECT mes::DATE AS mes
    FROM limites, generate_series(inicio, fim, INTERVAL '1 month') AS meses(mes)
), resumo AS (
    SELECT date_trunc('month', data_evento)::DATE AS mes,
           count(*) AS eventos_corte,
           count(postos_contabilizados) AS eventos_quantificados,
           sum(postos_contabilizados) AS postos_contabilizados
    FROM cortes
    GROUP BY 1
)
SELECT c.mes,
       coalesce(r.eventos_corte, 0) AS eventos_corte,
       coalesce(r.eventos_quantificados, 0) AS eventos_quantificados,
       r.postos_contabilizados
FROM calendario AS c
LEFT JOIN resumo AS r ON r.mes = c.mes
ORDER BY c.mes
