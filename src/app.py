from flask import Flask, request, render_template, url_for
app = Flask(__name__, static_folder='frontend/static', template_folder='frontend/templates')

@app.route('/')
def home():
    return render_template('index.html')
    # word = request.args.get('query', '')
    # data = 'This is a sample publication'
    # return render_template('index.html', query=word, results=data)

@app.route('/publications')
def publications():
    return render_template('publications.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)