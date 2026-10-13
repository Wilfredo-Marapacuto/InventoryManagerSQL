"""Inventory Manager SQL.

A console application for practicing relational databases and SQL.
Use fictional records while learning and demonstrating the application.
"""

import math
import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "inventory.db"

PRODUCT_QUERY = """
    SELECT p.product_id, p.name, p.quantity, p.unit_price,
           s.name AS supplier_name
    FROM products AS p
    INNER JOIN suppliers AS s
        ON p.supplier_id = s.supplier_id
"""


def create_connection():
    """Open the database and enable foreign-key enforcement."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables(connection):
    """Create related tables with keys and validation constraints."""
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL CHECK(length(trim(name)) > 0),
            contact TEXT NOT NULL CHECK(length(trim(contact)) > 0)
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL CHECK(length(trim(name)) > 0),
            quantity INTEGER NOT NULL CHECK(quantity >= 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            supplier_id INTEGER NOT NULL,
            FOREIGN KEY (supplier_id)
                REFERENCES suppliers(supplier_id)
                ON DELETE RESTRICT
        );
    """)
    connection.commit()


def read_text(prompt):
    """Require a nonempty text value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a value.")


def read_integer(prompt, minimum=0):
    """Require an integer at or above the specified minimum."""
    while True:
        try:
            value = int(input(prompt))
            if value >= minimum:
                return value
        except ValueError:
            pass
        print(f"Enter a whole number of at least {minimum}.")


def read_price(prompt):
    """Require a finite, nonnegative price with at most two decimals."""
    while True:
        try:
            value = float(input(prompt))
            if math.isfinite(value) and value >= 0:
                return round(value, 2)
        except ValueError:
            pass
        print("Enter a nonnegative price, such as 12.50.")


def list_suppliers(connection):
    """Retrieve suppliers and display their IDs and contact details."""
    rows = connection.execute("""
        SELECT supplier_id, name, contact
        FROM suppliers
        ORDER BY supplier_id
    """).fetchall()

    if not rows:
        print("No suppliers found.")
        return False

    print("\nSUPPLIERS")
    for row in rows:
        print(
            f"ID: {row['supplier_id']} | "
            f"Name: {row['name']} | "
            f"Contact: {row['contact']}"
        )
    return True


def add_supplier(connection):
    """Insert a supplier using bound parameters and commit the change."""
    name = read_text("Supplier name: ")
    contact = read_text("Supplier contact: ")

    with connection:
        cursor = connection.execute(
            "INSERT INTO suppliers (name, contact) VALUES (?, ?)",
            (name, contact),
        )

    print(f"Supplier added. ID: {cursor.lastrowid}")


def add_product(connection):
    """Validate a supplier and insert a product linked to that supplier."""
    if not list_suppliers(connection):
        print("Add a supplier before adding a product.")
        return

    supplier_id = read_integer("Supplier ID: ", minimum=1)
    supplier = connection.execute(
        "SELECT supplier_id FROM suppliers WHERE supplier_id = ?",
        (supplier_id,),
    ).fetchone()

    if supplier is None:
        print("Supplier ID not found.")
        return

    name = read_text("Product name: ")
    quantity = read_integer("Quantity: ")
    price = read_price("Unit price: ")

    with connection:
        cursor = connection.execute("""
            INSERT INTO products
                (name, quantity, unit_price, supplier_id)
            VALUES (?, ?, ?, ?)
        """, (name, quantity, price, supplier_id))

    print(f"Product added. ID: {cursor.lastrowid}")


def display_products(rows):
    """Format retrieved products, including their joined supplier names."""
    if not rows:
        print("No matching products.")
        return

    print("\nINVENTORY")
    for row in rows:
        value = row["quantity"] * row["unit_price"]
        print(
            f"ID: {row['product_id']} | "
            f"Name: {row['name']} | "
            f"Quantity: {row['quantity']} | "
            f"Price: ${row['unit_price']:.2f} | "
            f"Supplier: {row['supplier_name']} | "
            f"Value: ${value:.2f}"
        )


def list_products(connection):
    """List all products using an INNER JOIN with suppliers."""
    rows = connection.execute(
        PRODUCT_QUERY + " ORDER BY p.product_id"
    ).fetchall()
    display_products(rows)


def search_products(connection):
    """Find products whose names contain the user's search text."""
    term = read_text("Search product name: ")
    rows = connection.execute(
        PRODUCT_QUERY
        + " WHERE instr(lower(p.name), lower(?)) > 0"
        + " ORDER BY p.name",
        (term,),
    ).fetchall()
    display_products(rows)


def low_stock_report(connection):
    """List products below a user-selected stock threshold."""
    threshold = read_integer("Show quantities below: ")
    rows = connection.execute(
        PRODUCT_QUERY
        + " WHERE p.quantity < ?"
        + " ORDER BY p.quantity, p.product_id",
        (threshold,),
    ).fetchall()
    display_products(rows)


def update_product(connection):
    """Update either a product's quantity or its unit price."""
    product_id = read_integer("Product ID to update: ", minimum=1)
    product = connection.execute(
        "SELECT * FROM products WHERE product_id = ?",
        (product_id,),
    ).fetchone()

    if product is None:
        print("Product ID not found.")
        return

    print(
        f"Selected: {product['name']} | "
        f"Quantity: {product['quantity']} | "
        f"Price: ${product['unit_price']:.2f}"
    )
    print("1. Update quantity")
    print("2. Update unit price")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        quantity = read_integer("New quantity: ")
        with connection:
            connection.execute(
                "UPDATE products SET quantity = ? WHERE product_id = ?",
                (quantity, product_id),
            )
    elif choice == "2":
        price = read_price("New unit price: ")
        with connection:
            connection.execute(
                "UPDATE products SET unit_price = ? WHERE product_id = ?",
                (price, product_id),
            )
    else:
        print("Invalid option. No changes made.")
        return

    print("Product updated successfully.")


def delete_product(connection):
    """Delete an existing product only after explicit confirmation."""
    product_id = read_integer("Product ID to delete: ", minimum=1)
    product = connection.execute(
        "SELECT name FROM products WHERE product_id = ?",
        (product_id,),
    ).fetchone()

    if product is None:
        print("Product ID not found.")
        return

    confirmation = input(
        f"Delete {product['name']}? Type YES to confirm: "
    ).strip()

    if confirmation != "YES":
        print("Deletion canceled.")
        return

    with connection:
        connection.execute(
            "DELETE FROM products WHERE product_id = ?",
            (product_id,),
        )

    print("Product deleted successfully.")


def delete_supplier(connection):
    """Delete a supplier unless foreign-key restrictions prevent it."""
    if not list_suppliers(connection):
        return

    supplier_id = read_integer("Supplier ID to delete: ", minimum=1)
    supplier = connection.execute(
        "SELECT name FROM suppliers WHERE supplier_id = ?",
        (supplier_id,),
    ).fetchone()

    if supplier is None:
        print("Supplier ID not found.")
        return

    confirmation = input(
        f"Delete {supplier['name']}? Type YES to confirm: "
    ).strip()

    if confirmation != "YES":
        print("Deletion canceled.")
        return

    try:
        with connection:
            connection.execute(
                "DELETE FROM suppliers WHERE supplier_id = ?",
                (supplier_id,),
            )
        print("Supplier deleted successfully.")
    except sqlite3.IntegrityError:
        print("Cannot delete a supplier that still has products.")


def inventory_summary(connection):
    """Use SQL aggregate functions to summarize inventory."""
    row = connection.execute("""
        SELECT COUNT(*) AS product_count,
               COALESCE(SUM(quantity), 0) AS total_units,
               COALESCE(SUM(quantity * unit_price), 0) AS total_value
        FROM products
    """).fetchone()

    print("\nINVENTORY SUMMARY")
    print(f"Product records: {row['product_count']}")
    print(f"Total units: {row['total_units']}")
    print(f"Total inventory value: ${row['total_value']:.2f}")


def main():
    """Initialize the database and process menu choices."""
    connection = create_connection()

    try:
        create_tables(connection)
        actions = {
            "1": add_supplier,
            "2": list_suppliers,
            "3": add_product,
            "4": list_products,
            "5": update_product,
            "6": delete_product,
            "7": search_products,
            "8": low_stock_report,
            "9": inventory_summary,
            "10": delete_supplier,
        }

        while True:
            print("\n===== INVENTORY MANAGER SQL =====")
            print("1. Add supplier")
            print("2. List suppliers")
            print("3. Add product")
            print("4. List products")
            print("5. Update product")
            print("6. Delete product")
            print("7. Search products")
            print("8. Low-stock report")
            print("9. Inventory summary")
            print("10. Delete supplier")
            print("0. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "0":
                print("Goodbye. Saved changes remain in inventory.db.")
                break

            action = actions.get(choice)
            if action is None:
                print("Invalid option. Please try again.")
                continue

            try:
                action(connection)
            except sqlite3.Error as error:
                print(f"Database operation failed: {error}")

    except (KeyboardInterrupt, EOFError):
        print("\nApplication closed.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()