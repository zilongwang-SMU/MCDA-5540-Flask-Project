# MySQL Database Setup Instructions

## Prerequisites

1. MySQL Server installed and running
2. Python 3.x installed

## Setup Steps

### 1. Install Required Packages

```powershell
pip install mysql-connector-python
```

### 2. Create MySQL Database

Open MySQL command line or MySQL Workbench and run:

```sql
CREATE DATABASE flask_db;
```

### 3. Configure Database Connection

Edit `project.py` and update the `DB_CONFIG` dictionary (lines 10-15) with your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',        # Your MySQL host (usually 'localhost')
    'user': 'root',             # Your MySQL username
    'password': 'your_password', # Your MySQL password
    'database': 'flask_db'      # Your database name
}
```

### 4. Run the Application

```powershell
python project.py
```

The application will:

- Automatically create all required tables
- Insert sample data on first run
- Start the Flask development server at http://127.0.0.1:5000/

## Database Schema

The application creates the following tables:

- **employees** - Store employee information
- **dependents** - Store employee dependents (Foreign Key to employees)
- **projects** - Store project information
- **expenses** - Store project expenses (Foreign Key to projects)
- **products** - Store product information
- **reviews** - Store product reviews (Foreign Key to products)

## Features

1. **Show Tables** - View all database tables and their contents
2. **Add New Data** - Insert data into multiple related tables
3. **Data Analysis** - Budget projections and product performance analytics

## Troubleshooting

### Connection Error

If you get a connection error:

- Verify MySQL server is running
- Check username and password in `DB_CONFIG`
- Ensure the database `flask_db` exists
- Check firewall settings

### Module Not Found Error

```powershell
pip install -r requirements.txt
```

### Port Already in Use

If port 5000 is already in use, modify the last line in `project.py`:

```python
app.run(debug=True, port=5001)  # Change port number
```
