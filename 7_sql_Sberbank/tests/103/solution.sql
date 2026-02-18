-- Сотрудники, у которых зарплата больше, чем у непосредственного руководителя
SELECT e.name
FROM employees e
INNER JOIN employees chief ON e.chief_id = chief.id
WHERE e.salary > chief.salary
ORDER BY e.name;
