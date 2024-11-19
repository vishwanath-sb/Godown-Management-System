import pymysql
from flask import Flask, render_template, request, redirect, flash, jsonify
from config import create_connection
from datetime import date
import mysql.connector
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Helper function to run database queries
def run_query(query, params=None):
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall() if cursor.with_rows else None
            # conn.commit()
            cursor.close()
            conn.close()
            return result or []  # Return an empty list if result is None
        else:
            return []  # Return empty list if connection fails
    except mysql.connector.Error as err:
        print("Error:", err)
        return []  # Return empty list in case of query error

# Home page route
@app.route("/")
def home():
    return render_template("index.html")

# Display list of products in different warehouses
@app.route("/products")
def list_products():
    products_query = "CALL GetProducts();"
    costly_product_query = "CALL GetMostCostlyProduct();"
    
    products = run_query(products_query)
    most_costly_product = run_query(costly_product_query)

    # Assuming `most_costly_product` returns a single row
    most_costly_product = most_costly_product[0] if most_costly_product else None

    return render_template(
        "products.html", 
        products=products, 
        most_costly_product=most_costly_product
    )


@app.route("/sell")
def supplier_product_map():
    # Query for Supplier-Product Relationship Map
    supplier_query = """
        SELECT s.Name AS SupplierName, p.Availability, p.Name AS ProductName, p.Category
        FROM Suppliers s
        JOIN SupplierProducts sp ON s.SupplierID = sp.SupplierID
        JOIN Products p ON sp.ProductID = p.ProductID
        ORDER BY s.Name, p.Name;
    """
    supplier_product_data = run_query(supplier_query)

    # Query for Order Details
    order_details_query = """
        SELECT c.Name AS CustomerName, o.OrderDate, od.Quantity, p.Name AS ProductName
        FROM OrderDetails od
        JOIN Orders o ON od.OrderID = o.OrderID
        JOIN Customers c ON o.CustomerID = c.CustomerID
        JOIN Products p ON od.ProductID = p.ProductID
        ORDER BY o.OrderDate DESC, c.Name;
    """
    order_details_data = run_query(order_details_query)

    return render_template("sell.html", supplier_product_data=supplier_product_data, order_details_data=order_details_data)




@app.route("/orders", methods=["GET", "POST"])
def place_order():
    if request.method == "POST":
        customer_id = request.form["customer_id"]
        order_date = request.form["order_date"]

        # Get lists of selected products and corresponding quantities
        products = request.form.getlist("product_id")
        quantities = request.form.getlist("quantity")

        # Connect to MySQL database
        connection = create_connection()
        try:
            cursor = connection.cursor()
            # Start transaction
            connection.start_transaction()

            # Insert order
            insert_order_query = "INSERT INTO Orders (CustomerID, OrderDate) VALUES (%s, %s)"
            cursor.execute(insert_order_query, (customer_id, order_date))

            # Get the OrderID of the newly inserted order
            cursor.execute("SELECT LAST_INSERT_ID() AS id")
            order_id = cursor.fetchone()[0]

            # Check if products are available and insert order details
            for product_id, quantity in zip(products, quantities):
                # Check product availability
                check_availability_query = "SELECT Availability FROM Products WHERE ProductID = %s"
                cursor.execute(check_availability_query, (product_id,))
                available_quantity = cursor.fetchone()

                if available_quantity and int(quantity) <= available_quantity[0]:
                    # Insert order details into OrderDetails table
                    insert_order_details_query = "INSERT INTO OrderDetails (OrderID, ProductID, Quantity) VALUES (%s, %s, %s)"
                    cursor.execute(insert_order_details_query, (order_id, product_id, int(quantity)))

                    # # Update product availability only once
                    # update_availability_query = "UPDATE Products SET Availability = Availability - %s WHERE ProductID = (%s)/2"
                    # cursor.execute(update_availability_query, (int(quantity), product_id))
                else:
                    flash(f"Error: Insufficient quantity for product ID {product_id}")
                    connection.rollback()
                    return redirect("/orders")

            # Commit transaction if all queries are successful
            connection.commit()
            flash("Order placed successfully!")
            return redirect("/orders")
        except mysql.connector.Error as e:
            # Rollback if any error occurs
            connection.rollback()
            flash(f"Error: Unable to place order! {e}")
            print("Error:", e)
        finally:
            cursor.close()
            connection.close()

    # Get all products for the order form
    products_query = "SELECT ProductID, Name FROM Products WHERE Availability > 0"
    products = run_query(products_query)

    # Get all customers for the customer dropdown
    customers_query = "SELECT CustomerID, Name FROM Customers"
    customers = run_query(customers_query)

    return render_template("orders.html", products=products, customers=customers)






@app.route("/reports")
def reports():
    # Query to get products by warehouse
    query = """
        SELECT w.name AS WarehouseName, w.location AS WarehouseLocation, 
               p.ProductID, p.Name AS ProductName, p.Category, p.mfg_date, 
               p.exp_date, p.PricePerUnit, p.Availability
        FROM Warehouses w
        LEFT JOIN Products p ON w.WarehouseID = p.WarehouseID
        ORDER BY w.name;
    """
    warehouse_products = run_query(query)
    
    # Organize products by warehouse
    warehouses = {}
    for row in warehouse_products:
        warehouse_name = row['WarehouseName']
        if warehouse_name not in warehouses:
            warehouses[warehouse_name] = {
                "location": row["WarehouseLocation"],
                "products": []
            }
        warehouses[warehouse_name]["products"].append(row)
    
    return render_template("reports.html", warehouses=warehouses)



# Assume run_query is already defined as a function for database operations

@app.route("/add_supplier", methods=["GET", "POST"])
def add_supplier():
    if request.method == "POST":
        # Step 1: Gather form data
        supplier_name = request.form["supplier_name"]
        contact_info = request.form["contact_info"]
        
        product_name = request.form["product_name"]
        category = request.form["category"]
        quantity = request.form["quantity"]
        cost_per_unit = request.form["cost_per_unit"]
        supply_date = request.form["supply_date"]
        mfg_date = request.form["mfg_date"]
        exp_date = request.form["exp_date"]
        price_per_unit = request.form["price_per_unit"]
        warehouse_id = request.form["warehouse_id"]
        availability = request.form["availability"]

        # Start a transaction
        connection = pymysql.connect(host='localhost', user='root', password='PES1UG22CS704', db='godown_management')
        try:
            with connection.cursor() as cursor:
                # Begin transaction
                connection.begin()

                # Insert Supplier
                supplier_query = "INSERT INTO Suppliers (Name, ContactInfo) VALUES (%s, %s)"
                cursor.execute(supplier_query, (supplier_name, contact_info))
                # Get SupplierID of newly added supplier
                supplier_id = cursor.lastrowid

                # Insert Product
                product_query = """
                    INSERT INTO Products (Name, Category, mfg_date, exp_date, PricePerUnit, Availability, WarehouseID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(product_query, (product_name, category, mfg_date, exp_date, price_per_unit, availability, warehouse_id))
                # Get ProductID of newly added product
                product_id = cursor.lastrowid

                # Insert into SupplierProducts table
                supplier_product_query = """
                    INSERT INTO SupplierProducts (SupplierID, ProductID, Quantity, CostPerUnit, SupplyDate)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(supplier_product_query, (supplier_id, product_id, quantity, cost_per_unit, supply_date))

                # Commit transaction
                connection.commit()

            # Success message and redirect
            flash("Supplier and Product added successfully!")
            return redirect("/add_supplier")
        except Exception as e:
            # Rollback transaction in case of error
            connection.rollback()
            flash(f"Error: {str(e)}")
            return redirect("/add_supplier")
        finally:
            connection.close()

    # Render template and pass warehouse list for the dropdown
    warehouses = run_query("SELECT WarehouseID, Name FROM Warehouses")
    return render_template("add_supplier.html", warehouses=warehouses)






# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
