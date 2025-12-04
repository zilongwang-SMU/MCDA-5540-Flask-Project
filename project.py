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
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 1000")
        rows = cursor.fetchall()
        columns = list(rows[0].keys()) if rows else []
        cursor.close()
        conn.close()
        return columns, rows
    except Error as e:
        print(f"Error fetching table data for {table_name}: {e}")
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
    message = None
    tables = get_all_tables()
    selected_table = None
    table_columns = None

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'error')
            return redirect(url_for('add_data'))

        cursor = conn.cursor()
        try:
            if form_type == 'employee':
                # Insert employee and optionally dependent in a transaction
                name = request.form.get('emp_name')
                position = request.form.get('emp_position')
                hire_date = request.form.get('emp_hire_date') or None
                salary = request.form.get('emp_salary') or 0

                cursor.execute('START TRANSACTION')
                cursor.execute('INSERT INTO employees (name, position, hire_date, salary) VALUES (%s,%s,%s,%s)',
                               (name, position, hire_date, salary))
                emp_id = cursor.lastrowid

                dep_name = request.form.get('dep_name')
                dep_relation = request.form.get('dep_relation')
                if dep_name:
                    cursor.execute('INSERT INTO dependents (employee_id, name, relation) VALUES (%s,%s,%s)',
                                   (emp_id, dep_name, dep_relation))

                conn.commit()
                flash('Employee (and dependent) added successfully', 'success')

            elif form_type == 'expense':
                year = int(request.form.get('exp_year'))
                category = request.form.get('exp_category')
                amount = float(request.form.get('exp_amount') or 0)
                cursor.execute('INSERT INTO expenses (year, category, amount) VALUES (%s,%s,%s)',
                               (year, category, amount))
                conn.commit()
                flash('Expense added successfully', 'success')

            elif form_type == 'deliverable':
                name = request.form.get('deliv_name')
                dtype = request.form.get('deliv_type')
                score = request.form.get('review_score')
                comment = request.form.get('review_comment')

                cursor.execute('START TRANSACTION')
                cursor.execute('INSERT INTO deliverables (name, type) VALUES (%s,%s)', (name, dtype))
                deliv_id = cursor.lastrowid
                if score:
                    cursor.execute('INSERT INTO reviews (deliverable_id, score, comment) VALUES (%s,%s,%s)',
                                   (deliv_id, int(score), comment))
                conn.commit()
                flash('Deliverable and review added successfully', 'success')

            elif form_type == 'generic':
                # Generic insert into any table selected by user
                table_name = request.form.get('table_name')
                if not table_name:
                    raise Error('No table specified for generic insert')

                # fetch columns to insert (skip auto_increment)
                cursor.execute('''
                    SELECT COLUMN_NAME, IS_NULLABLE, EXTRA
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
                    ORDER BY ORDINAL_POSITION
                ''', (DB_CONFIG['database'], table_name))
                cols_meta = cursor.fetchall()
                insert_cols = []
                values = []
                for cm in cols_meta:
                    colname = cm[0]
                    extra = cm[2] or ''
                    is_nullable = cm[1]
                    if 'auto_increment' in extra.lower():
                        continue
                    # Read posted value
                    v = request.form.get(f'col_{colname}')
                    if v == '':
                        # convert empty string to None if column allows NULL
                        v = None if is_nullable == 'YES' else ''
                    insert_cols.append(colname)
                    values.append(v)

                if not insert_cols:
                    raise Error('No insertable columns detected for table')

                placeholders = ','.join(['%s'] * len(insert_cols))
                cols_sql = ','.join([f'`{c}`' for c in insert_cols])
                sql = f'INSERT INTO `{table_name}` ({cols_sql}) VALUES ({placeholders})'
                cursor.execute(sql, tuple(values))
                conn.commit()
                flash(f'Row inserted into {table_name}', 'success')

            else:
                flash('Unknown form submission', 'error')

        except Error as e:
            conn.rollback()
            flash(f'Error inserting data: {e}', 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('add_data'))
    # GET: possibly show dynamic insert form for selected table
    if request.method == 'GET':
        selected_table = request.args.get('table')
        if selected_table:
            # fetch column metadata from INFORMATION_SCHEMA
            conn = get_db_connection()
            if conn:
                cur = conn.cursor(dictionary=True)
                try:
                    cur.execute('''
                        SELECT COLUMN_NAME, DATA_TYPE, COLUMN_KEY, IS_NULLABLE, EXTRA
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
                        ORDER BY ORDINAL_POSITION
                    ''', (DB_CONFIG['database'], selected_table))
                    table_columns = cur.fetchall()
                except Error as e:
                    flash(f'Error fetching table schema: {e}', 'error')
                finally:
                    cur.close()
                    conn.close()

    return render_template('add_data.html', tables=tables, selected_table=selected_table, table_columns=table_columns)

# Route 4: Data Analysis (Function 3)
@app.route("/analysis", methods=['GET', 'POST'])
def analysis():
    tables = get_all_tables()
    result = None

    if request.method == 'POST':
        analysis_type = request.form.get('analysis_type')
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'error')
            return redirect(url_for('analysis'))

        cursor = conn.cursor(dictionary=True)
        try:
            if analysis_type == 'forecast':
                # Forecast next 3 years total expenses given an inflation rate
                inflation = float(request.form.get('inflation') or 0) / 100.0
                cursor.execute('SELECT year, SUM(amount) as total FROM expenses GROUP BY year ORDER BY year')
                rows = cursor.fetchall()
                years = [r['year'] for r in rows]
                totals = {r['year']: float(r['total']) for r in rows}

                if not years:
                    flash('No expense data available for forecasting', 'error')
                else:
                    last_year = max(years)
                    last_total = totals[last_year]
                    projections = []
                    for i in range(1,4):
                        proj = last_total * ((1 + inflation) ** i)
                        projections.append({'year': last_year + i, 'projected_total': round(proj,2)})

                    result = {'type':'forecast','base_year': last_year,'base_total': round(last_total,2),'projections': projections}

            elif analysis_type == 'top_n':
                n = int(request.form.get('n') or 5)
                mode = request.form.get('mode') or 'best'
                cursor.execute('''
                    SELECT d.id, d.name, d.type, AVG(r.score) as avg_score, COUNT(r.id) as reviews
                    FROM deliverables d
                    LEFT JOIN reviews r ON r.deliverable_id = d.id
                    GROUP BY d.id
                ''')
                rows = cursor.fetchall()
                # compute order
                rows_sorted = sorted(rows, key=lambda r: (r['avg_score'] if r['avg_score'] is not None else 0), reverse=(mode=='best'))
                rows_sorted = rows_sorted[:n]
                result = {'type':'top_n','mode':mode,'n':n,'items': rows_sorted}

        except Error as e:
            flash(f'Error running analysis: {e}', 'error')
        finally:
            cursor.close()
            conn.close()

        return render_template('analysis.html', tables=tables, result=result)

    return render_template('analysis.html', tables=tables)

if __name__ == "__main__":
    print("Starting Flask application...")
    # Initialize demo tables and data, then test connection
    check_db_connection()
    app.run(debug=True)