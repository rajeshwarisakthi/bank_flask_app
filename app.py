from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from decimal import Decimal
import os

app = Flask(__name__)
app.secret_key = "bank_secret_key"

# ---------------- Database Connection ----------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",         # Update if using remote DB
        user="root",              # Your MySQL username
        password="Rajisakthi@0912",  # Your MySQL password
        database="bankdb"
    )

# ---------------- Home Page ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- Customers Page ----------------
@app.route('/customers', methods=['GET', 'POST'])
def customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        dob = request.form['dob']

        cursor.execute("""
            INSERT INTO Customer (name, address, phone, email, dob)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, address, phone, email, dob))
        conn.commit()
        flash("✅ New customer added successfully!", "success")

    cursor.execute("SELECT * FROM Customer ORDER BY customer_id DESC")
    customers = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)


# ---------------- Accounts Page ----------------
@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        account_type = request.form['account_type'].strip().capitalize()
        balance = Decimal(request.form['balance'])

        if account_type not in ['Savings', 'Checking', 'Loan']:
            flash("❌ Invalid account type! Choose 'Savings', 'Checking', or 'Loan'.", "danger")
        else:
            cursor.execute("""
                INSERT INTO Account (customer_id, account_type, balance)
                VALUES (%s, %s, %s)
            """, (customer_id, account_type, balance))
            conn.commit()
            flash("✅ Account created successfully!", "success")

    cursor.execute("SELECT customer_id, name FROM Customer")
    customers = cursor.fetchall()

    cursor.execute("""
        SELECT a.account_id, c.name AS customer_name, a.account_type, a.balance
        FROM Account a
        JOIN Customer c ON a.customer_id = c.customer_id
        ORDER BY a.account_id DESC
    """)
    accounts = cursor.fetchall()
    conn.close()
    return render_template('accounts.html', accounts=accounts, customers=customers)


# ---------------- Transactions Page ----------------
@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        account_id = request.form['account_id']
        transaction_type = request.form['transaction_type']
        amount = Decimal(request.form['amount'])

        cursor.execute("SELECT balance FROM Account WHERE account_id = %s", (account_id,))
        result = cursor.fetchone()

        if not result:
            flash("❌ Invalid Account ID!", "danger")
            conn.close()
            return redirect(url_for('transactions'))

        balance = result['balance']

        if transaction_type == 'Deposit':
            new_balance = balance + amount
        elif transaction_type == 'Withdraw':
            if balance < amount:
                flash("⚠️ Insufficient funds!", "warning")
                conn.close()
                return redirect(url_for('transactions'))
            new_balance = balance - amount
        else:
            flash("❌ Invalid transaction type!", "danger")
            conn.close()
            return redirect(url_for('transactions'))

        cursor.execute("UPDATE Account SET balance = %s WHERE account_id = %s", (new_balance, account_id))
        cursor.execute("""
            INSERT INTO Transactions (account_id, transaction_type, amount, transaction_date)
            VALUES (%s, %s, %s, NOW())
        """, (account_id, transaction_type, amount))
        conn.commit()
        flash("✅ Transaction completed successfully!", "success")

    cursor.execute("SELECT account_id, account_type FROM Account ORDER BY account_id")
    accounts = cursor.fetchall()

    cursor.execute("""
        SELECT t.transaction_id, t.account_id, a.account_type,
               t.transaction_type, t.amount, t.transaction_date
        FROM Transactions t
        JOIN Account a ON t.account_id = a.account_id
        ORDER BY t.transaction_date DESC
    """)
    transactions = cursor.fetchall()
    conn.close()
    return render_template('transactions.html', accounts=accounts, transactions=transactions)


# ---------------- Employees Page ----------------
@app.route('/employees', methods=['GET', 'POST'])
def employees():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        salary = Decimal(request.form['salary'])

        cursor.execute("""
            INSERT INTO Employee (name, role, salary)
            VALUES (%s, %s, %s)
        """, (name, role, salary))
        conn.commit()
        flash("✅ Employee added successfully!", "success")

    cursor.execute("SELECT * FROM Employee ORDER BY employee_id DESC")
    employees = cursor.fetchall()
    conn.close()
    return render_template('employees.html', employees=employees)


# ---------------- Run Flask App ----------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use env PORT if available
    app.run(host='0.0.0.0', port=port, debug=True)
