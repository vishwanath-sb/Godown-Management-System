# Godown Management System

A warehouse (godown) management system designed to track inventory, manage suppliers and customers, and handle orders efficiently. The system uses **MySQL** for the database and integrates with a **Flask** backend for seamless operations.

---

## Features

- **Warehouse Management**: Track multiple warehouses with details like location and associated products.
- **Product Management**: Maintain product information, including category, manufacturing/expiration dates, price per unit, and stock availability.
- **Supplier Integration**: Manage suppliers and the products they supply.
- **Order Management**: Allow customers to place orders, update inventory automatically, and ensure availability validation.
- **Stored Procedures**:
  - `GetProducts`: Retrieve all product details.
  - `GetMostCostlyProduct`: Identify the most expensive product in the database.
- **Trigger**:
  - Automatically decrements product availability after an order is placed.

---

## Database Schema

- **Warehouses**
- **Products**
- **Suppliers**
- **SupplierProducts**
- **Customers**
- **Orders**
- **OrderDetails**

Refer to the `schema.sql` file for the complete database structure.

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/vishwanath-sb/Godown-Management-System.git
   cd Godown-Management-System
