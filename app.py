import os
import psycopg2
from flask import Flask

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )
    return conn

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if table exists, create if it doesn't
        cur.execute("SELECT to_regclass('public.visits');")
        if cur.fetchone()[0] is None:
            cur.execute("CREATE TABLE visits (id serial PRIMARY KEY, visit_time timestamp NOT NULL DEFAULT NOW());")
            conn.commit()

        # Insert a new visit
        cur.execute("INSERT INTO visits (visit_time) VALUES (NOW());")
        conn.commit()
        
        # Count visits
        cur.execute('SELECT COUNT(*) FROM visits;')
        visits = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return f"<h1>歡迎！</h1><p>您是第 {visits} 位訪客。</p>"
    except Exception as e:
        return f"<h1>連線錯誤</h1><p>無法連線到資料庫：{e}</p>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
