from flask import Flask, request, render_template, url_for
import sqlite3
import os

app = Flask(__name__, static_folder='frontend/static', template_folder='frontend/templates')

# Resolve database path relative to this file
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasets', 'cbdata.sqlite'))

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Make sure the file exists and the path is correct.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    # return render_template('index.html')
    word = request.args.get('query', '')
    data = 'This is a sample publication'
    return render_template('index.html', query=word, results=data)

@app.route('/publications')
def publications():
    conn = get_db_connection()
    try:
        data = conn.execute('SELECT * FROM Publications').fetchall()
    finally:
        conn.close()
    columns = data[0].keys() if data else []
    return render_template('publications.html', display=data, columns=columns)

@app.route('/datasets')
def datasets():
    conn = get_db_connection()
    try:
        data = conn.execute('SELECT * FROM Datasets').fetchall()
    finally:
        conn.close()
    columns = data[0].keys() if data else []
    return render_template('datasets.html', display=data, columns=columns)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)