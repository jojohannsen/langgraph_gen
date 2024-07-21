from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows all origins

# Variable to store the latest graph
latest_graph = ""

@app.route('/')
def index():
    return render_template('graph_editor.html')

@app.route('/update_graph', methods=['POST'])
def update_graph():
    global latest_graph
    data = request.json
    print(data)
    latest_graph = data.get('graph', '')
    print("Received graph update:")
    print(latest_graph)
    return jsonify({"status": "success", "message": "Graph updated"})

if __name__ == '__main__':
    app.run(debug=True)
