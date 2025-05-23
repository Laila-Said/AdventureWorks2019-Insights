--overall trend of monthly and yearly revenue--
SELECT 
    YEAR(OrderDate) AS OrderYear,
    MONTH(OrderDate) AS OrderMonth,
    SUM(TotalDue) AS MonthlyRevenue
FROM Sales.SalesOrderHeader
GROUP BY YEAR(OrderDate), MONTH(OrderDate)
ORDER BY OrderYear, OrderMonth


SELECT YEAR(OrderDate) AS OrderYear, SUM(TotalDue) AS YearlyRevenue
FROM Sales.SalesOrderHeader
GROUP BY YEAR(OrderDate) 
ORDER BY YearlyRevenue DESC;
--the overall trend isn't stable--


SELECT pc.Name AS CategoryName, SUM(soh.TotalDue) AS TotalRevenue
FROM Sales.SalesOrderHeader AS soh
JOIN Sales.SalesOrderDetail AS sod 
ON soh.SalesOrderID = sod.SalesOrderID
JOIN Production.Product AS p ON sod.ProductID = p.ProductID
JOIN Production.ProductSubcategory AS psc 
ON p.ProductSubcategoryID = psc.ProductSubcategoryID
JOIN Production.ProductCategory AS pc 
ON psc.ProductCategoryID = pc.ProductCategoryID
GROUP BY pc.Name
ORDER BY TotalRevenue DESC;
---

SELECT psc.Name AS SubcategoryName, SUM(soh.TotalDue) AS TotalRevenue
FROM Sales.SalesOrderHeader AS soh
JOIN Sales.SalesOrderDetail AS sod 
ON soh.SalesOrderID = sod.SalesOrderID
JOIN Production.Product AS p 
ON sod.ProductID = p.ProductID
JOIN Production.ProductSubcategory AS psc 
ON p.ProductSubcategoryID = psc.ProductSubcategoryID
GROUP BY psc.Name
ORDER BY TotalRevenue DESC;
--- Bikes specifically Road bikes contribute the most to the total revenue --- 


WITH CategoryRevenue AS (
SELECT pc.Name AS CategoryName, SUM(soh.TotalDue) AS TotalRevenue
FROM Sales.SalesOrderHeader AS soh
JOIN Sales.SalesOrderDetail AS sod 
ON soh.SalesOrderID = sod.SalesOrderID
JOIN Production.Product AS p 
ON sod.ProductID = p.ProductID
JOIN Production.ProductSubcategory AS psc 
ON p.ProductSubcategoryID = psc.ProductSubcategoryID
JOIN Production.ProductCategory AS pc 
ON psc.ProductCategoryID = pc.ProductCategoryID
GROUP BY pc.Name
)
---
SELECT 
    CategoryName,
    TotalRevenue
FROM 
    CategoryRevenue
WHERE 
    TotalRevenue < (SELECT AVG(TotalRevenue) * 0.5 FROM CategoryRevenue)
ORDER BY 
    TotalRevenue;
--- Accessories is underperforming category ---

----
SELECT 
    st.Name AS TerritoryName,
    SUM(soh.TotalDue) AS TotalRevenue
FROM Sales.SalesOrderHeader AS soh
JOIN Sales.SalesTerritory AS st 
ON soh.TerritoryID = st.TerritoryID
GROUP BY st.Name
ORDER BY TotalRevenue DESC;
-- southwest is the most profitable territory --

---
SELECT 
    YEAR(OrderDate) AS OrderYear,
    MONTH(OrderDate) AS OrderMonth,
    COUNT(SalesOrderID) AS TotalOrders,
    COUNT(SalesOrderID) / COUNT(DISTINCT MONTH(OrderDate)) AS AverageOrdersPerMonth
FROM Sales.SalesOrderHeader
GROUP BY YEAR(OrderDate), MONTH(OrderDate)
ORDER BY OrderYear, OrderMonth;
---
SELECT 
    YEAR(OrderDate) AS OrderYear,
    COUNT(SalesOrderID) AS TotalOrders,
    COUNT(SalesOrderID) / COUNT(DISTINCT YEAR(OrderDate)) AS AverageOrdersPerYear
FROM Sales.SalesOrderHeader
GROUP BY YEAR(OrderDate)
ORDER BY OrderYear;
--sales orders are processed on average per month/year--

---

--What is the customer retention rate? How can it be improved?--
WITH FirstOrders AS (
    SELECT 
        CustomerID,
        MIN(OrderDate) AS FirstOrderDate
    FROM Sales.SalesOrderHeader
    GROUP BY CustomerID
)
SELECT * FROM FirstOrders;

SELECT * FROM Sales.SalesOrderHeader;

-----------------------------------------------------------------------
WITH FirstOrders AS (
    SELECT CustomerID, MIN(OrderDate) AS FirstOrderDate
    FROM Sales.SalesOrderHeader
    GROUP BY CustomerID
),
FirstTimeCustomers2011 AS (
    SELECT 
        CustomerID
    FROM FirstOrders
    WHERE YEAR(FirstOrderDate) = 2011
)

SELECT * FROM FirstTimeCustomers2011;
---------------------------------------------------------------------



WITH FirstOrders AS (
    SELECT 
        CustomerID,
        MIN(OrderDate) AS FirstOrderDate
    FROM Sales.SalesOrderHeader
    GROUP BY CustomerID
),
FirstTimeCustomers2021 AS (
    SELECT 
        CustomerID
    FROM FirstOrders
    WHERE YEAR(FirstOrderDate) = 2021
)

Returning Customers AS (
    SELECT DISTINCT soh.CustomerID
    FROM Sales.SalesOrderHeader soh
    JOIN FirstTimeCustomers2021 ftc ON soh.CustomerID = ftc.CustomerID
    WHERE YEAR(soh.OrderDate) = 2022
)
SELECT * FROM ReturningCustomers2022;

)

SELECT 
    COUNT(*) AS TotalCustomers2021,
    (SELECT COUNT(*) FROM ReturningCustomers2022) AS ReturnedIn2022,
    ROUND(
        (SELECT COUNT(*) FROM ReturningCustomers2022) * 1.0 /
        COUNT(*) * 100, 2
    ) AS RetentionRatePercent
FROM FirstTimeCustomers2021;

-------------------------------------------------------------
----------------------------------------------------------------
----------------------------------------------------------------
WITH FirstOrders AS (
    SELECT 
        CustomerID,
        MIN(OrderDate) AS FirstOrderDate
    FROM Sales.SalesOrderHeader
    GROUP BY CustomerID
),

FirstTimeCustomers2011 AS (
    SELECT 
        fo.CustomerID
    FROM FirstOrders fo
    WHERE YEAR(fo.FirstOrderDate) = 2011
),

ReturningCustomers2012 AS (
    SELECT DISTINCT soh.CustomerID
    FROM Sales.SalesOrderHeader soh
    JOIN FirstTimeCustomers2011 ftc ON soh.CustomerID = ftc.CustomerID
    WHERE YEAR(soh.OrderDate) = 2012
)


SELECT 
    COUNT(*) AS TotalCustomers2011,
    (SELECT COUNT(*) FROM ReturningCustomers2012) AS ReturnedIn2012,
    ROUND(
        (SELECT COUNT(*) FROM ReturningCustomers2012) * 1.0 /
        COUNT(*) * 100, 2
    ) AS RetentionRatePercent
FROM FirstTimeCustomers2011;
--------------------------------------------------------------------
---------------------------------
---------------------------------------------------------------------
---------------------------------------------------------------------
--How frequently do customers make purchases on average? --
WITH CustomerOrders AS (
    SELECT 
        CustomerID,
        COUNT(*) AS OrderCount
    FROM Sales.SalesOrderHeader
    GROUP BY CustomerID
)

SELECT 
    AVG(OrderCount * 1.0) AS AvgOrdersPerCustomer
FROM CustomerOrders;
------------------------------------------------------------
----------------------------------------------------------------
---------------------------------------------------------------

----------------------------------------------------------------
--Are there different purchase frequencies among different customer segments?--
WITH CustomerOrders AS (
    SELECT 
        c.CustomerID,
        CASE 
            WHEN c.StoreID IS NULL THEN 'Individual'
            ELSE 'Store'
        END AS CustomerType,
        COUNT(*) AS OrderCount
    FROM Sales.SalesOrderHeader soh
    JOIN Sales.Customer c ON soh.CustomerID = c.CustomerID
    GROUP BY c.CustomerID, c.StoreID
)

SELECT 
    CustomerType,
    COUNT(*) AS TotalCustomers,
    AVG(OrderCount * 1.0) AS AvgOrdersPerCustomer
FROM CustomerOrders
GROUP BY CustomerType;
----------------------------
WITH CustomerOrders AS (
    SELECT 
        c.CustomerID,
        st.Name AS Territory,
        COUNT(*) AS OrderCount
    FROM Sales.SalesOrderHeader soh
    JOIN Sales.Customer c ON soh.CustomerID = c.CustomerID
    JOIN Sales.SalesTerritory st ON soh.TerritoryID = st.TerritoryID
    GROUP BY c.CustomerID, st.Name
)

SELECT 
    Territory,
    COUNT(*) AS TotalCustomers,
    AVG(OrderCount * 1.0) AS AvgOrdersPerCustomer
FROM CustomerOrders
GROUP BY Territory
ORDER BY AvgOrdersPerCustomer DESC;
---------------------------------------------------
----------------------------------------------------
------------------------------------------------------
-------------------------------------------------------------
--Can we identify distinct customer segments based on their purchasing behavior?--
WITH CustomerSummary AS (
    SELECT 
        soh.CustomerID,
        COUNT(*) AS OrderCount,
        SUM(soh.TotalDue) AS TotalSpent
    FROM Sales.SalesOrderHeader soh
    GROUP BY soh.CustomerID
),
SegmentedCustomers AS (
    SELECT 
        CustomerID,
        OrderCount,
        TotalSpent,
        CASE 
            WHEN TotalSpent >= 10000 THEN 'High Value'
            WHEN TotalSpent BETWEEN 5000 AND 9999 THEN 'Mid Value'
            ELSE 'Low Value'
        END AS ValueSegment
    FROM CustomerSummary
)
SELECT 
    ValueSegment,
    COUNT(*) AS NumCustomers,
    ROUND(AVG(OrderCount * 1.0), 2) AS AvgOrders,
    ROUND(AVG(TotalSpent), 2) AS AvgSpent
FROM SegmentedCustomers
GROUP BY ValueSegment;
-----------------------------------
WITH CustomerFrequency AS (
    SELECT 
        CustomerID,
        COUNT(*) AS OrderCount
    FROM Sales.SalesOrderHeader
    GROUP BY CustomerID
),
Segmented AS (
    SELECT 
        CustomerID,
        OrderCount,
        CASE 
            WHEN OrderCount >= 10 THEN 'Frequent Buyer'
            WHEN OrderCount BETWEEN 5 AND 9 THEN 'Moderate Buyer'
            ELSE 'Occasional Buyer'
        END AS FrequencySegment
    FROM CustomerFrequency
)
SELECT FrequencySegment, COUNT(*) AS NumCustomers
FROM Segmented
GROUP BY FrequencySegment;


SELECT TOP 1
    p.Name AS ProductName,
    SUM(sd.OrderQty) AS TotalUnitsSold
FROM Sales.SalesOrderDetail sd
JOIN Production.Product p ON sd.ProductID = p.ProductID
GROUP BY p.Name
ORDER BY TotalUnitsSold DESC;
----------------------------------------------------------------
SELECT TOP 1
    p.Name AS ProductName,
    SUM(sd.LineTotal) AS TotalRevenue
FROM Sales.SalesOrderDetail sd
JOIN Production.Product p ON sd.ProductID = p.ProductID
GROUP BY p.Name
ORDER BY TotalRevenue DESC;
-----------------------------------------------------------------
SELECT 
    pc.Name AS CategoryName,
    AVG(p.ListPrice) AS AvgSellingPrice
FROM Production.Product p
JOIN Production.ProductSubcategory psc ON p.ProductSubcategoryID = psc.ProductSubcategoryID
JOIN Production.ProductCategory pc ON psc.ProductCategoryID = pc.ProductCategoryID
WHERE p.ListPrice > 0
GROUP BY pc.Name
ORDER BY AvgSellingPrice DESC;
---------------------------------------------------------------------
WITH MonthlySales AS (
    SELECT 
        p.Name AS ProductName,
        YEAR(soh.OrderDate) AS SalesYear,
        MONTH(soh.OrderDate) AS SalesMonth,
        SUM(sod.OrderQty) AS TotalMonthlySales
    FROM Sales.SalesOrderHeader AS soh
    JOIN Sales.SalesOrderDetail AS sod ON soh.SalesOrderID = sod.SalesOrderID
    JOIN Production.Product AS p ON sod.ProductID = p.ProductID
    GROUP BY p.Name, YEAR(soh.OrderDate), MONTH(soh.OrderDate)
),
LowSalesProducts AS (
    SELECT 
        ProductName,
        COUNT(*) AS LowSalesMonths,
        COUNT(*) * 1.0 / (SELECT COUNT(DISTINCT YEAR(OrderDate)*12 + MONTH(OrderDate)) FROM Sales.SalesOrderHeader) AS LowSalesRatio
    FROM MonthlySales
    WHERE TotalMonthlySales < 10 -- threshold: products selling < 10 units per month
    GROUP BY ProductName
)
SELECT 
    ProductName,
    LowSalesMonths,
    CAST(LowSalesRatio * 100 AS DECIMAL(5,2)) AS LowSalesPercentage
FROM LowSalesProducts
WHERE LowSalesMonths >= 1 -- consider "consistently low" if low for 3+ months
ORDER BY LowSalesMonths DESC;
