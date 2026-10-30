-- Grão: empresa com postos contabilizados em cortes. Acumulado sobre o total conhecido.
-- Agregar antes da janela; desempatar por empresa para manter a exportação estável.
WITH empresas AS (
    SELECT empresa, sum(postos_contabilizados) AS postos_contabilizados
    FROM refined.eventos
    WHERE tipo_evento = 'cut' AND postos_contabilizados IS NOT NULL
    GROUP BY empresa
)
SELECT empresa, postos_contabilizados,
       row_number() OVER (ORDER BY postos_contabilizados DESC, empresa) AS posicao,
       round(100.0 * sum(postos_contabilizados) OVER (
           ORDER BY postos_contabilizados DESC, empresa
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) / nullif(sum(postos_contabilizados) OVER (), 0), 2) AS pct_acumulado
FROM empresas
ORDER BY posicao
