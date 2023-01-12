from flask import Blueprint, render_template, request, flash, redirect, jsonify, json
from flask_login import current_user, login_user, LoginManager, logout_user, login_required
from models import User, db, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/sign_in', methods=['POST'])
def sign_in():
    try:
        email = request.json['email']
        password = request.json['password']
        logged_user = User.query.filter_by(email = email).first()
        print(logged_user)
        if logged_user and check_password_hash(logged_user.password, password):
            login_user(logged_user)
            return jsonify({'email': logged_user.email, 'token': logged_user.token, 'name': logged_user.name, 'password': password, 'id': current_user.id})
        else:
            return jsonify({'message': 'incorrect information'})
    except:
        return jsonify({'message': 'invalid input'})


@auth.route('/sign_up', methods=['POST', 'GET'])
def register():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    if name and '@' in email and password:
        check_user = User.query.filter_by(email = email).first()
        if not check_user:
            user = User(name = name, email = email, password = password)
            login_user(user)
            db.session.add(user)
            db.session.commit()
            print(user)
            return jsonify({'email': user.email, 'token': user.token, 'name': user.name, 'password': password, 'id': current_user.id})
        else:
            return jsonify({'message': 'User taken'})
    else:
        return jsonify({'message': 'invalid input'})

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return jsonify({'message': 'You have been successfully logged out'})