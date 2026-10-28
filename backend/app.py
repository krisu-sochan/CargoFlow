from flask import Flask
app = Flask(__name__)
@app.route('/api/health', methods=['GET'])
def health():
    return {'status': 'ok','message': 'Service is running'}, 200