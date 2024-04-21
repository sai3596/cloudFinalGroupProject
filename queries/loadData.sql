SELECT
DISTINCT
    hh.HSHD_NUM,
    txns.BASKET_NUM,
    txns.PURCHASE_,
    txns.PRODUCT_NUM,
    p.DEPARTMENT,
    p.COMMODITY,
    txns.SPEND,
    txns.UNITS,
    txns.STORE_R,
    txns.WEEK_NUM,
    txns.YEAR_NUM,
    hh.L,
    hh.AGE_RANGE,
    hh.MARITAL,
    hh.INCOME_RANGE,
    hh.HOMEOWNER,
    hh.HSHD_COMPOSITION,
    hh.HH_SIZE,
    hh.CHILDREN
FROM
    households as hh
INNER JOIN
    transactions as txns
INNER JOIN
    products as p
ON
    hh.HSHD_NUM=txns.HSHD_NUM
AND
    txns.PRODUCT_NUM=p.PRODUCT_NUM
WHERE
    hh.HSHD_NUM={}
ORDER BY
    hh.HSHD_NUM,
    txns.BASKET_NUM,
    txns.PURCHASE_,
    txns.PRODUCT_NUM,
    p.DEPARTMENT,
    p.COMMODITY;