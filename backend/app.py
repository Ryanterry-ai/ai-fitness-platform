
from flask import Flask, request, jsonify
from backend.search_ai import search_knowledge

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q')
    results = search_knowledge(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run()
