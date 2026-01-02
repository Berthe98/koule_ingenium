from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' 

# --- CONFIGURATION ---
ADMIN_USERNAME = "BERTHE FADEL" 
ADMIN_PASSWORD = "4BTH1998"      

# Define the absolute path to your database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'content_data.db')

def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH) 
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates required tables if they do not exist in the database."""
    conn = get_db_connection()
    # Create services table
    conn.execute('''CREATE TABLE IF NOT EXISTS services 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, icon TEXT, title TEXT, description TEXT)''')
    # Create events table
    conn.execute('''CREATE TABLE IF NOT EXISTS events 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, event_date TEXT, description TEXT)''')
    # Create news table
    conn.execute('''CREATE TABLE IF NOT EXISTS news 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date TEXT, content TEXT)''')
    conn.commit()
    conn.close()

# Run database initialization once when the app starts
init_db()

# --- PUBLIC ROUTES ---

@app.route('/')
def index():
    conn = get_db_connection()
    services = conn.execute('SELECT * FROM services').fetchall() 
    news = conn.execute('SELECT * FROM news ORDER BY date DESC').fetchall() 
    events = conn.execute('SELECT * FROM events ORDER BY event_date ASC').fetchall()
    conn.close()
    return render_template('index.html', services=services, news=news, events=events)

# --- AUTHENTICATION ---

@app.route('/login', methods=['POST'])
def login():
    data = request.json 
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True 
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

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
    services = conn.execute('SELECT * FROM services').fetchall()
    events = conn.execute('SELECT * FROM events ORDER BY event_date ASC').fetchall()
    conn.close()
    
    return render_template('admin.html', services=services, events=events)

# --- CRUD OPERATIONS ---

@app.route('/add_service', methods=['POST'])
def add_service():
    if not session.get('logged_in'): return redirect('/admin')
    data = request.form
    conn = get_db_connection()
    conn.execute('INSERT INTO services (icon, title, description) VALUES (?, ?, ?)',
                 (data['icon'], data['title'], data['description']))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_portal'))

@app.route('/edit_service/<int:id>')
def edit_service_page(id):
    if not session.get('logged_in'): return redirect('/admin')
    conn = get_db_connection()
    service = conn.execute('SELECT * FROM services WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_service.html', service=service)

@app.route('/update_service/<int:id>', methods=['POST'])
def update_service(id):
    if not session.get('logged_in'): return redirect('/admin')
    conn = get_db_connection()
    conn.execute('UPDATE services SET icon = ?, title = ?, description = ? WHERE id = ?',
                 (request.form['icon'], request.form['title'], request.form['description'], id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_portal'))

@app.route('/delete_service/<int:id>', methods=['POST'])
def delete_service(id):
    if not session.get('logged_in'): return redirect('/admin')
    conn = get_db_connection()
    conn.execute('DELETE FROM services WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_portal'))

@app.route('/add_event', methods=['POST'])
def add_event():
    if not session.get('logged_in'): return redirect('/admin')
    conn = get_db_connection()
    conn.execute('INSERT INTO events (title, event_date, description) VALUES (?, ?, ?)',
                 (request.form['event_title'], request.form['event_date'], request.form['event_desc']))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_portal'))

@app.route('/delete_event/<int:id>', methods=['POST'])
def delete_event(id):
    if not session.get('logged_in'): return redirect('/admin')
    conn = get_db_connection()
    conn.execute('DELETE FROM events WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_portal'))

# --- SERVER STARTUP ---

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)