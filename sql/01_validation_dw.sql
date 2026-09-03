-- ============================================================
-- VALIDATION DU DATA WAREHOUSE
-- Maven Electronics
-- ============================================================


-- ============================================================
-- TEST 1 : Vérification du nombre de lignes
-- ============================================================

SELECT 'dim_date' AS table_name, COUNT(*) AS nb_lignes
FROM dim_date

UNION ALL

SELECT 'dim_customer', COUNT(*)
FROM dim_customer

UNION ALL

SELECT 'dim_product', COUNT(*)
FROM dim_product

UNION ALL

SELECT 'dim_store', COUNT(*)
FROM dim_store

UNION ALL

SELECT 'dim_exchange_rate', COUNT(*)
FROM dim_exchange_rate

UNION ALL

SELECT 'fact_sales', COUNT(*)
FROM fact_sales;


-- ============================================================
-- TEST 2 : Vérification des doublons dans Dim_Customer
-- Résultat attendu : 0 ligne
-- ============================================================

SELECT customer_key, COUNT(*)
FROM dim_customer
GROUP BY customer_key
HAVING COUNT(*) > 1;


-- ============================================================
-- TEST 3 : Vérification des doublons dans Dim_Product
-- Résultat attendu : 0 ligne
-- ============================================================

SELECT product_key, COUNT(*)
FROM dim_product
GROUP BY product_key
HAVING COUNT(*) > 1;


-- ============================================================
-- TEST 4 : Vérification des doublons dans Dim_Store
-- Résultat attendu : 0 ligne
-- ============================================================

SELECT store_key, COUNT(*)
FROM dim_store
GROUP BY store_key
HAVING COUNT(*) > 1;


-- ============================================================
-- TEST 5 : Vérification des doublons dans Dim_Date
-- Résultat attendu : 0 ligne
-- ============================================================

SELECT date_key, COUNT(*)
FROM dim_date
GROUP BY date_key
HAVING COUNT(*) > 1;


-- ============================================================
-- TEST 6 : Fact_Sales sans client correspondant
-- Résultat attendu : 0
-- ============================================================

SELECT COUNT(*) AS ventes_sans_client
FROM fact_sales f
LEFT JOIN dim_customer c
    ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL;


-- ============================================================
-- TEST 7 : Fact_Sales sans produit correspondant
-- Résultat attendu : 0
-- ============================================================

SELECT COUNT(*) AS ventes_sans_produit
FROM fact_sales f
LEFT JOIN dim_product p
    ON f.product_key = p.product_key
WHERE p.product_key IS NULL;


-- ============================================================
-- TEST 8 : Fact_Sales sans magasin correspondant
-- Résultat attendu : 0
-- ============================================================

SELECT COUNT(*) AS ventes_sans_magasin
FROM fact_sales f
LEFT JOIN dim_store s
    ON f.store_key = s.store_key
WHERE s.store_key IS NULL;


-- ============================================================
-- TEST 9 : Fact_Sales sans date de commande correspondante
-- Résultat attendu : 0
-- ============================================================

SELECT COUNT(*) AS ventes_sans_date_commande
FROM fact_sales f
LEFT JOIN dim_date d
    ON f.order_date_key = d.date_key
WHERE d.date_key IS NULL;


-- ============================================================
-- TEST 10 : Dates de livraison invalides
-- Résultat attendu : 0
-- ============================================================

SELECT COUNT(*) AS livraisons_sans_date_dimension
FROM fact_sales f
LEFT JOIN dim_date d
    ON f.delivery_date_key = d.date_key
WHERE f.delivery_date_key IS NOT NULL
  AND d.date_key IS NULL;


-- ============================================================
-- TEST 11 : Vérification de la granularité de Fact_Sales
-- Une combinaison Order Number + Line Item doit être unique
-- Résultat attendu : 0 ligne
-- ============================================================

SELECT
    order_number,
    line_item,
    COUNT(*) AS nb
FROM fact_sales
GROUP BY order_number, line_item
HAVING COUNT(*) > 1;


-- ============================================================
-- TEST 12 : Statistiques générales des ventes
-- ============================================================

SELECT
    COUNT(*) AS nb_lignes_vente,
    COUNT(DISTINCT order_number) AS nb_commandes,
    SUM(quantity) AS quantite_totale,
    MIN(order_date_key) AS premiere_date,
    MAX(order_date_key) AS derniere_date
FROM fact_sales;