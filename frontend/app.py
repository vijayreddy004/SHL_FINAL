from flask import Flask, render_template, request, jsonify
import requests
app = Flask(__name__)
BACKEND_URL = "http://localhost:8000/recommend"
STYLES = """
:root {
    --black-900: #0a0a0a;
    --black-800: #1a1a1a;
    --accent: #00ff88;
    --text-primary: #e0e0e0;
}
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}
body {
    background-color: var(--black-900);
    color: var(--text-primary);
    font-family: 'Inter', system-ui, sans-serif;
    min-height: 100vh;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}
.header {
    text-align: center;
    margin-bottom: 3rem;
}
.title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(45deg, var(--accent), #00ccff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 1rem;
}
.search-container {
    max-width: 600px;
    margin: 0 auto 3rem;
}
.search-form {
    position: relative;
}
.search-input {
    width: 100%;
    padding: 1rem 2rem;
    background: var(--black-800);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 50px;
    color: white;
    font-size: 1rem;
    transition: all 0.3s ease;
}
.search-input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.1);
}
.results-container {
    display: grid;
    gap: 2rem;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}
.card {
    background: var(--black-800);
    border-radius: 16px;
    padding: 1.5rem;
    transition: transform 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.card:hover {
    transform: translateY(-5px);
}
.card-title {
    font-size: 1.25rem;
    margin-bottom: 1rem;
    color: var(--accent);
}
.meta-item {
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    opacity: 0.8;
}
.loading {
    text-align: center;
    padding: 2rem;
    font-size: 1.2rem;
    color: var(--accent);
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeIn 0.4s ease forwards;
}
"""
@app.route('/')
def home():
    return render_template('index.html', styles=STYLES)
@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    try:
        response = requests.post(
            f"{BACKEND_URL}",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(port=5000, debug=True)