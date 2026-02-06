from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    with sqlite3.connect('database.db') as conn:
        # Added 'date' column to the table
        conn.execute('''CREATE TABLE IF NOT EXISTS expenses 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         item TEXT, amount REAL, category TEXT, date TEXT)''')

@app.route('/')
def index():
    # Get filter and sort parameters from the URL
    cat_filter = request.args.get('category', 'All')
    sort_by = request.args.get('sort', 'newest')

    query = "SELECT * FROM expenses"
    params = []

    if cat_filter != 'All':
        query += " WHERE category = ?"
        params.append(cat_filter)

    if sort_by == 'high':
        query += " ORDER BY amount DESC"
    elif sort_by == 'low':
        query += " ORDER BY amount ASC"
    else:
        query += " ORDER BY date DESC"

    with sqlite3.connect('database.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Get unique categories for the filter dropdown
        cursor.execute("SELECT DISTINCT category FROM expenses")
        categories = [r['category'] for r in cursor.fetchall()]
        
        total = sum(row['amount'] for row in rows)

    return render_template('index.html', expenses=rows, total=total, categories=categories)

@app.route('/add', methods=['POST'])
def add():
    item = request.form['item']
    amount = float(request.form['amount'])
    # User can type their own category now
    category = request.form['category'].strip().capitalize()
    date = request.form.get('date') or datetime.now().strftime('%Y-%m-%d')
    
    with sqlite3.connect('database.db') as conn:
        conn.execute('INSERT INTO expenses (item, amount, category, date) VALUES (?, ?, ?, ?)', 
                     (item, amount, category, date))
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    with sqlite3.connect('database.db') as conn:
        conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)