from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'zilong',  # Try with root user
    'password': 'wzl1415167038',
    'database': 'test',
    'port': 3306,
    'charset': 'utf8mb4',
    'use_unicode': True
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            charset=DB_CONFIG['charset'],
            use_unicode=DB_CONFIG['use_unicode']
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Check database connection
def check_db_connection():
    """Check if database connection is working"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        print("Database connection successful!")
        return True
    except Error as e:
        print(f"Database connection test failed: {e}")
        if conn:
            conn.close()
        return False

def get_all_tables():
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables

def get_table_data(table_name):
    conn = get_db_connection()
    if not conn:
        return None, None
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = list(rows[0].keys()) if rows else []
        cursor.close()
        conn.close()
        return columns, rows
    except Error as e:
        print(f"Error: {e}")
        cursor.close()
        conn.close()
        return None, None

# Route 1: Home page with navigation
@app.route("/")
def index():
    return render_template('index.html')

# Route 2: Show Table (Function 1)
@app.route("/show_table", methods=['GET', 'POST'])
def show_table():
    tables = get_all_tables()
    selected_table = None
    columns = None
    data = None
    
    if request.method == 'POST':
        selected_table = request.form.get('table_name')
        if selected_table:
            columns, data = get_table_data(selected_table)
    
    return render_template('show_table.html', 
                         tables=tables, 
                         selected_table=selected_table,
                         columns=columns,
                         data=data)

# Route 3: Add New Data (Function 2)
@app.route("/add_data", methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        # Get all tables to allow dynamic insertion
        tables = get_all_tables()
        
        # This is a placeholder - you can customize based on your actual tables
        flash('Add data functionality ready - customize based on your database tables', 'success')
        return redirect(url_for('add_data'))
    
    # Get list of tables for display
    tables = get_all_tables()
    return render_template('add_data.html', tables=tables)

# Route 4: Data Analysis (Function 3)
@app.route("/analysis", methods=['GET', 'POST'])
def analysis():
    # Placeholder for custom analysis based on your actual database tables
    tables = get_all_tables()
    return render_template('analysis.html', tables=tables)

if __name__ == "__main__":
    print("Starting Flask application...")
    check_db_connection()
    app.run(debug=True)