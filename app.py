import os 
import psutil
import sqlite3
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- DATABASE LOGIC ---

DB_PATH = os.path.join(BASE_DIR, 'data', 'monitor.db')

def get_db_connection():
    # Ensure the directory exists before connecting
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cpu REAL,
                ram REAL
            )
        ''')
        conn.commit()

# --- BACKGROUND TASKS (ETL) ---
def save_automatic_stats():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO logs (cpu, ram) VALUES (?, ?)', (cpu, ram))
        conn.commit()
    print(f"[*] Automatic record saved: CPU {cpu}% | RAM {ram}%")

# Configure the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=save_automatic_stats, trigger="interval", minutes=10)
scheduler.start()

init_db()

# --- ROUTES ---
@app.route('/')
def home():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    
    stats = {
        'cpu': cpu_usage,
        'ram': ram_usage,
        'status': 'Healthy' if cpu_usage < 80 else 'Critical'
    }
    return render_template('index.html', stats=stats)

@app.route('/logs')
def logs():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT fecha, cpu, ram FROM logs ORDER BY id DESC')
        data = cursor.fetchall()
    return render_template('logs.html', logs=data)

if __name__ == '__main__':
    try:
        app.run(debug=True, port=5000, use_reloader=False) # use_reloader=False prevents the scheduler from running twice
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()