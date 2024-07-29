from flask import request, jsonify, render_template_string, redirect, url_for, session
import jwt
from datetime import datetime, timedelta
from models import User, Message
from extensions import db

def register_routes(app):
    @app.route('/')
    def index():
        return render_template_string(open('homepageIndex.html').read())

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            data = request.get_json()  # Ensure this reads JSON data
            if data is None:
                return jsonify({'message': 'Invalid data format, expected JSON'}), 400
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            if not username or not email or not password:
                return jsonify({'message': 'All fields are required'}), 400
            
            if User.query.filter_by(email=email).first():
                return jsonify({'message': 'Email already registered'}), 400
            
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({'message': 'User registered successfully'}), 201
        return render_template_string(open('registerForm.html').read())

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            data = request.get_json()
            if data is None:
                return jsonify({'message': 'Invalid data format, expected JSON'}), 400

            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'message': 'All fields are required'}), 400
            
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)}, app.config['SECRET_KEY'])
                return jsonify({'token': token})
            return jsonify({'message': 'Invalid credentials'}), 401
        return render_template_string(open('login.html').read())

    @app.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():
        token = session.get('token')
        if not token:
            return redirect(url_for('login'))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid'}), 403

        if request.method == 'POST':
            receiver_id = request.form['receiver_id']
            content = request.form['message']
            new_message = Message(sender_id=data['user_id'], receiver_id=receiver_id, content=content)
            db.session.add(new_message)
            db.session.commit()
            return redirect(url_for('dashboard'))
        
        messages = Message.query.filter((Message.sender_id == data['user_id']) | (Message.receiver_id == data['user_id'])).all()
        return render_template('chatInterface.html', messages=messages)

    @app.route('/logout')
    def logout():
        session.pop('token', None)
        return redirect(url_for('login'))
