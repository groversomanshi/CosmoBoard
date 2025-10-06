from flask import Flask, request, render_template, url_for, jsonify
import sqlite3
import os
import csv
import sys

# Add the backend directory to the path to import recommender
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from recommender import paper_detail, similar_papers, search_papers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_folder='frontend/static', template_folder='frontend/templates')

# Resolve database path relative to this file
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasets', 'cbdata.sqlite'))

# @app.route('/static/style.css')
# def serve_static(filename):
#     return app.send_static_file(filename)

@app.context_processor
def inject_stage_prefix():
    return dict(stage_prefix='/Dev')

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Make sure the file exists and the path is correct.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    # return render_template('index.html')
    word = request.args.get('query', '').lower()
    data = []

    if word:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # find keyword id
            cur.execute('SELECT id FROM Keywords WHERE keyword=?', (word,))
            kw_row = cur.fetchone()
            if kw_row:
                kw_id = kw_row['id'] if isinstance(kw_row, dict) or hasattr(kw_row, '__getitem__') else kw_row[0]
                # fetch references for that keyword id with publication and dataset details
                cur.execute('''
                    SELECT r.id, r.publication_id, r.dataset_id, 
                           p.title as pub_title, p.id as pmcid,
                           d.title as dataset_name, d.id as dataset_id
                    FROM Referencing r
                    LEFT JOIN Publications p ON r.publication_id = p.id
                    LEFT JOIN Datasets d ON r.dataset_id = d.id
                    WHERE r.keyword_id=?
                ''', (kw_id,))
                data = cur.fetchall()
            else:
                data = []
        finally:
            conn.close()
    columns = data[0].keys() if data else []
    return render_template('index.html', query=word, display=data, columns=columns)

@app.route('/publications')
def publications():
    conn = get_db_connection()
    try:
        data = conn.execute('SELECT * FROM Publications').fetchall()
        titles = [row['title'] for row in data]
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

@app.route('/publication/<pmcid>')
def publication_detail(pmcid):
    """Display detailed information about a specific publication with ML recommendations"""
    try:
        # First get basic info from database
        conn = get_db_connection()
        try:
            db_pub = conn.execute('SELECT * FROM Publications WHERE id = ?', (pmcid,)).fetchone()
            if not db_pub:
                return render_template('error.html', message=f"Publication {pmcid} not found in database")
        finally:
            conn.close()
        
        # Get detailed info and recommendations from CSV files using ML model
        paper_data = paper_detail(pmcid, k_similar=5)
        
        if 'error' in paper_data:
            # If not found in CSV, use database info only
            return render_template('publication_detail.html', 
                                 paper={'pmcid': pmcid, 'title': db_pub['title'], 'paper_url': None},
                                 similar_papers=[],
                                 datasets=[])
        
        return render_template('publication_detail.html', 
                             paper=paper_data,
                             similar_papers=paper_data['similar'],
                             datasets=paper_data['datasets'])
    except Exception as e:
        return render_template('error.html', message=f"Error loading publication: {str(e)}")

@app.route('/dataset/<dataset_id>')
def dataset_detail(dataset_id):
    """Display detailed information about a specific dataset"""
    conn = get_db_connection()
    try:
        # Get dataset information from database
        dataset = conn.execute('SELECT * FROM Datasets WHERE id = ?', (dataset_id,)).fetchone()
        
        if not dataset:
            return render_template('error.html', message=f"Dataset {dataset_id} not found")
        
        # Get related publications for this dataset from database
        related_pubs = conn.execute('''
            SELECT DISTINCT p.* FROM Publications p
            JOIN Referencing r ON p.id = r.publication_id
            JOIN Datasets d ON d.id = r.dataset_id
            WHERE d.id = ?
        ''', (dataset_id,)).fetchall()
        
        # Try to get additional info from CSV files if available
        csv_datasets = []
        try:
            # Look for this dataset in the CSV files
            import pandas as pd
            links_df = pd.read_csv(os.path.join(BASE_DIR, 'datasets', 'paper_to_datasets.csv'))
            csv_links = links_df[links_df['dataset_id'] == dataset_id]
            if not csv_links.empty:
                csv_datasets = csv_links.to_dict('records')
        except:
            pass
        
        return render_template('dataset_detail.html', 
                             dataset=dataset,
                             related_publications=related_pubs,
                             csv_datasets=csv_datasets)
    except Exception as e:
        return render_template('error.html', message=f"Error loading dataset: {str(e)}")
    finally:
        conn.close()

@app.route('/api/recommendations/<pmcid>')
def get_recommendations(pmcid):
    """API endpoint to get ML recommendations for a publication"""
    try:
        recommendations = similar_papers(pmcid, k=5)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)