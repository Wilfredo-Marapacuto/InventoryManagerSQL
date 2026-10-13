# Overview

My goal with Inventory Manager SQL is to practice integrating a Python
application with a relational database. The project explores database
relationships, SQL queries, input validation, and persistent storage.

Inventory Manager SQL is a menu-driven application that manages suppliers
and products using SQLite. Users can add suppliers, add products, update
product quantities and prices, delete records, search products, and view
inventory reports.

To run the application on Windows, open a terminal in the project folder
and execute:

    py main.py

The application creates inventory.db automatically on its first run.
Start by adding a supplier, then add a product using that supplier's ID.
Choose menu options to manage records and generate reports. Select 0
to exit. Committed changes remain available when the application restarts.

The purpose of this software is to understand how Python sends SQL
commands to a database, retrieves results, and uses those results in
a practical inventory application. Development and demonstrations use
fictional records.

[Software Demo Video](https://youtu.be/BtNWtXkK4tA)

# Relational Database

The application uses SQLite, a relational database stored in the local
inventory.db file. Python accesses the database through the built-in
sqlite3 library.

The database contains two related tables:

## Suppliers

- supplier_id: INTEGER PRIMARY KEY identifying each supplier.
- name: Required, nonempty supplier name.
- contact: Required, nonempty contact information.

## Products

- product_id: INTEGER PRIMARY KEY identifying each product.
- name: Required, nonempty product name.
- quantity: Required integer with a nonnegative constraint.
- unit_price: Required numeric price with a nonnegative constraint.
- supplier_id: Required foreign key referencing suppliers.supplier_id.

One supplier can have multiple products. Foreign-key enforcement is
enabled when the application connects to the database. A supplier
cannot be deleted while products still reference it.

The application implements INSERT, UPDATE, DELETE, and SELECT.
User-provided values are passed through query parameters. Successful
changes are committed, and failed transactions are rolled back.

An INNER JOIN combines products and suppliers so inventory reports
display supplier names beside product details.

COUNT reports the number of product records. SUM reports total units
and total inventory value. COALESCE returns zero for aggregate totals
when the products table is empty.

# Development Environment

The application was run and tested using Visual Studio Code and
PowerShell on Windows with Python 3.14.2.

The program uses Python and these standard-library modules:

- sqlite3: Database connections, SQL execution, and transactions.
- pathlib: Locating inventory.db beside main.py.
- math: Rejecting nonfinite numeric prices.

No third-party Python packages are required.

# Useful Websites

- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite Foreign Key Documentation](https://www.sqlite.org/foreignkeys.html)
- [SQLite Aggregate Functions](https://www.sqlite.org/lang_aggfunc.html)

# Future Work

- Add options for editing product names and supplier contact information.
- Add inventory report exports to CSV.
- Store prices as integer cents to improve monetary precision.
- Add automated tests for database operations and input validation.