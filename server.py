from flask import Flask, render_template, request, jsonify, url_for, redirect
import sqlite3

app = Flask(__name__)
DB_NAME = "content_data.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize tables for Portfolio and Courses
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # Table for Portfolio/Projects
    cursor.execute('''CREATE TABLE IF NOT EXISTS portfolio 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, category TEXT, description TEXT, tags TEXT)''')
    # Table for Courses
    cursor.execute('''CREATE TABLE IF NOT EXISTS courses 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, level TEXT, price TEXT, duration TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    portfolio_items = conn.execute('SELECT * FROM portfolio').fetchall()
    courses = conn.execute('SELECT * FROM courses').fetchall()
    conn.close()
    return render_template('index.html', portfolio_items=portfolio_items, courses=courses)

@app.route('/admin')
def admin_dashboard():
    conn = get_db()
    portfolio = conn.execute('SELECT * FROM portfolio').fetchall()
    courses = conn.execute('SELECT * FROM courses').fetchall()
    conn.close()
    return render_template('admin.html', portfolio=portfolio, courses=courses)

# API to add/edit/delete (Simplified for your dashboard)
@app.route('/admin/add/<type>', methods=['POST'])
def add_entry(type):
    conn = get_db()
    if type == 'portfolio':
        conn.execute('INSERT INTO portfolio (title, category, description, tags) VALUES (?,?,?,?)',
                     (request.form['title'], request.form['category'], request.form['description'], request.form['tags']))
    elif type == 'course':
        conn.execute('INSERT INTO courses (title, level, price, duration) VALUES (?,?,?,?)',
                     (request.form['title'], request.form['level'], request.form['price'], request.form['duration']))
    conn.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<type>/<int:id>')
def delete_entry(type, id):
    conn = get_db()
    conn.execute(f'DELETE FROM {type} WHERE id = ?', (id,))
    conn.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)