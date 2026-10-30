-- Grão: família ocupacional entre cortes, com JOIN real entre as duas tabelas.
-- Cardinalidade: um evento para várias associações. Contagens NÃO são aditivas.
-- Não transportar nem somar postos depois da expansão das famílias.
SELECT f.familia_ocupacional,
       count(DISTINCT e.evento_id) AS eventos_corte
FROM refined.eventos AS e
JOIN refined.evento_familia AS f ON f.evento_id = e.evento_id
WHERE e.tipo_evento = 'cut'
GROUP BY f.familia_ocupacional
ORDER BY eventos_corte DESC, f.familia_ocupacional
