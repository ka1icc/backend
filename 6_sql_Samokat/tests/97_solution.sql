-- #97 Самокат: города с количеством работающих складов > 80 на текущую дату
-- Работающий склад: date_open <= текущая дата AND (date_close IS NULL OR date_close > текущая дата)

SELECT
    city,
    COUNT(*) AS warehouse_count
FROM warehouses
WHERE date_open <= CURRENT_DATE
  AND (date_close IS NULL OR date_close > CURRENT_DATE)
GROUP BY city
HAVING COUNT(*) > 80
ORDER BY warehouse_count DESC;
