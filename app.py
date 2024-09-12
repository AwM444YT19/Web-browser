from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Database configuration (using PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///browser.db'  # Use a local SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(255), nullable=False)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

# API Endpoints
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'User already exists'}), 400
    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        return jsonify({'message': 'Login successful'})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/bookmarks', methods=['GET', 'POST'])
def manage_bookmarks():
    if request.method == 'POST':
        data = request.json
        new_bookmark = Bookmark(user_id=data['user_id'], title=data['title'], url=data['url'])
        db.session.add(new_bookmark)
        db.session.commit()
        return jsonify({'message': 'Bookmark added successfully'})
    bookmarks = Bookmark.query.all()
    return jsonify([{'id': b.id, 'title': b.title, 'url': b.url} for b in bookmarks])

@app.route('/api/history', methods=['GET', 'POST'])
def manage_history():
    if request.method == 'POST':
        data = request.json
        timestamp = datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%S')  # Convert timestamp string to datetime object
        new_history = History(user_id=data['user_id'], url=data['url'], timestamp=timestamp)
        db.session.add(new_history)
        db.session.commit()
        return jsonify({'message': 'History added successfully'})
    history = History.query.all()
    return jsonify([{'id': h.id, 'url': h.url, 'timestamp': h.timestamp} for h in history])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(host='0.0.0.0', port=5000, debug=True)  # Run on port 5000
