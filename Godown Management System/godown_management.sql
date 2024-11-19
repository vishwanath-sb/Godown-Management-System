
CREATE DATABASE godown_management;
USE godown_management;


-- Table: Warehouses
CREATE TABLE Warehouses (
    WarehouseID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL,
    Location VARCHAR(100)
);

-- Table: Products
CREATE TABLE Products (
    ProductID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    mfg_date DATE NOT NULL,
    exp_date DATE NOT NULL,
    PricePerUnit DECIMAL(10, 2) NOT NULL,     -- Selling price per unit
    Availability INT DEFAULT 0,
    WarehouseID INT,
    FOREIGN KEY (WarehouseID) REFERENCES Warehouses(WarehouseID) ON DELETE SET NULL
);

-- Table: Suppliers
CREATE TABLE Suppliers (
    SupplierID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    ContactInfo VARCHAR(100)
);

-- Table: SupplierProducts
CREATE TABLE SupplierProducts (
    SupplierProductID INT PRIMARY KEY AUTO_INCREMENT,
    SupplierID INT,
    ProductID INT,
    Quantity INT NOT NULL,
    CostPerUnit DECIMAL(10, 2) NOT NULL,      -- Cost per unit from the supplier
    SupplyDate DATE NOT NULL,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE
);

-- Table: Customers
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    ContactInfo VARCHAR(100)
);

-- Table: Orders
CREATE TABLE Orders (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT,
    OrderDate DATE NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
);

-- Table: OrderDetails
CREATE TABLE OrderDetails (
    OrderDetailID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT,
    ProductID INT,
    Quantity INT NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE
);


DELIMITER //
CREATE TRIGGER after_order_insert
AFTER INSERT ON OrderDetails
FOR EACH ROW
BEGIN
    UPDATE Products
    SET Availability = Availability - NEW.Quantity
    WHERE ProductID = NEW.ProductID;
END;
//
DELIMITER ;

DELIMITER //

CREATE PROCEDURE GetProducts()
BEGIN
    SELECT p.ProductID, p.Name, p.Category, p.PricePerUnit, p.Availability, 
           p.mfg_date, p.exp_date, w.Name AS WarehouseName
    FROM Products p
    LEFT JOIN Warehouses w ON p.WarehouseID = w.WarehouseID;
END //

DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetMostCostlyProduct()
BEGIN
    SELECT 
        p.*, 
        w.Name AS WarehouseName
    FROM 
        Products p
    LEFT JOIN 
        Warehouses w ON p.WarehouseID = w.WarehouseID
    WHERE 
        p.PricePerUnit = (SELECT MAX(PricePerUnit) FROM Products);
END //
DELIMITER ;

