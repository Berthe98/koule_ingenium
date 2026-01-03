from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
import psycopg2
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' 

# --- CONFIGURATION ---
ADMIN_USERNAME = "BERTHE FADEL" 
ADMIN_PASSWORD = "4BTH1998"      

# 1. Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOCAL_DB_PATH = os.path.join(BASE_DIR, 'content_data.db')

def get_db_connection():
    if DATABASE_URL:
        # Connect to PostgreSQL (Render)
        url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(url, cursor_factory=DictCursor)
        return conn
    else:
        # Connect to SQLite (Local)
        conn = sqlite3.connect(LOCAL_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Creates tables and logs the status to the Render console."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        db_type = "PostgreSQL (Cloud)" if DATABASE_URL else "SQLite (Local)"
        
        queries = [
            '''CREATE TABLE IF NOT EXISTS services (id SERIAL PRIMARY KEY, icon TEXT, title TEXT, description TEXT)''',
            '''CREATE TABLE IF NOT EXISTS events (id SERIAL PRIMARY KEY, title TEXT, event_date TEXT, description TEXT)''',
            '''CREATE TABLE IF NOT EXISTS news (id SERIAL PRIMARY KEY, title TEXT, date TEXT, content TEXT)'''
        ]
        
        for q in queries:
            if not DATABASE_URL:
                q = q.replace('SERIAL', 'INTEGER PRIMARY KEY AUTOINCREMENT').replace('PRIMARY KEY', '')
            cur.execute(q)
            
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ DATABASE CONNECTED SUCCESSFULLY: Using {db_type}")
    except Exception as e:
        print(f"❌ DATABASE CONNECTION ERROR: {e}")

# Initialize on startup
init_db()

# --- ROUTES ---

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM services')
    services = cur.fetchall()
    cur.execute('SELECT * FROM news ORDER BY date DESC')
    news = cur.fetchall()
    cur.execute('SELECT * FROM events ORDER BY event_date ASC')
    events = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', services=services, news=news, events=events)

# --- AUTHENTICATION ---

@app.route('/login', methods=['POST'])
def login():
    data = request.json 
    if data.get('username') == ADMIN_USERNAME and data.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True 
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 401

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- ADMIN PANEL ---

@app.route('/admin')
def admin_portal():
    if not session.get('logged_in'):
        return redirect(url_for('index')) 
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM services')
    services = cur.fetchall()
    cur.execute('SELECT * FROM events ORDER BY event_date ASC')
    events = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', services=services, events=events)

# --- CRUD OPERATIONS ---

@app.route('/add_service', methods=['POST'])
def add_service():
    if not session.get('logged_in'): return redirect('/admin')
    placeholder = "%s" if DATABASE_URL else "?"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'INSERT INTO services (icon, title, description) VALUES ({placeholder}, {placeholder}, {placeholder})',
                 (request.form['icon'], request.form['title'], request.form['description']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_portal'))

@app.route('/delete_service/<int:id>', methods=['POST'])
def delete_service(id):
    if not session.get('logged_in'): return redirect('/admin')
    placeholder = "%s" if DATABASE_URL else "?"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'DELETE FROM services WHERE id = {placeholder}', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_portal'))

@app.route('/add_event', methods=['POST'])
def add_event():
    if not session.get('logged_in'): return redirect('/admin')
    placeholder = "%s" if DATABASE_URL else "?"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'INSERT INTO events (title, event_date, description) VALUES ({placeholder}, {placeholder}, {placeholder})',
                 (request.form['event_title'], request.form['event_date'], request.form['event_desc']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_portal'))

@app.route('/delete_event/<int:id>', methods=['POST'])
def delete_event(id):
    if not session.get('logged_in'): return redirect('/admin')
    placeholder = "%s" if DATABASE_URL else "?"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'DELETE FROM events WHERE id = {placeholder}', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_portal'))

# --- SERVER STARTUP ---

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)