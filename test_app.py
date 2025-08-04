from flask import Flask, jsonify
import sys
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "python_version": sys.version,
        "env_vars": {
            "DATABASE_URL": "SET" if os.environ.get("DATABASE_URL") else "NOT SET",
            "OPENAI_API_KEY": "SET" if os.environ.get("OPENAI_API_KEY") else "NOT SET",
            "WEBSITES_PORT": os.environ.get("WEBSITES_PORT", "NOT SET")
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)