from functools import wraps
from models import Book, User, db, book_schema, books_schema
from flask import jsonify, request, Blueprint, json
from flask_login import current_user, LoginManager, login_required
from werkzeug.security import generate_password_hash
from datetime import datetime

database_api = Blueprint('database_api', __name__, url_prefix='/api')

def token_required(flask_function):
    @wraps(flask_function)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            print(token)
        else:
            return jsonify({'message': 'No token found'})
        
        try:
            current_user_token = User.query.filter_by(token = token).first()
            if not current_user_token:
                raise Exception('Invalid token')
        except:
            return jsonify({'message': 'Invalid token'})
        return flask_function(current_user_token, *args, **kwargs)
    return decorated

@database_api.route('/add_book', methods=['POST', 'GET'])
@token_required
def add_book(current_user_token):
    try:
        author = request.json['author'][0]
        print(author)
        user_rating = request.json['user_rating']
        print(user_rating)
        if user_rating:
            user_rating = user_rating
        else:
            user_rating = 'You have not rated this book yet'
        average_rating = request.json['average_rating']

        if average_rating:
            average_rating = average_rating
        else:
            average_rating = 'Not yet rated'
        title = request.json['title']
        print(title)
        image_url = request.json['image_url']
        collection_status = request.json['collection_status']
        user_token = current_user_token.token
        print(collection_status)
        if Book.query.filter_by(title = title, user_token = user_token).first():
            return jsonify({'message': 'this book is already in your collection'})
        else:
            print('ok buddy')
            book = Book(user_rating = user_rating, title = title, author = author, user_token = user_token, average_rating = average_rating, image_url = image_url, collection_status = collection_status)
            print(book.date_holder)
            print(book.date_completed)
            db.session.add(book)
            db.session.commit()
            output = book_schema.dump(book)
            print(output)
            return jsonify(output)
    except:
        return jsonify({'message': 'failed error'})

@database_api.route('/view_books', methods=['GET', 'POST'])
@token_required
def get_books(current_user_token):
    filter = request.json['filter']
    if filter:
        all_books = Book.query.filter_by(collection_status = filter, user_token = current_user_token.token).all()
    else:
        all_books = Book.query.filter_by(user_token = current_user_token.token).all()
    if all_books:
        output = books_schema.dump(all_books)
        return jsonify(output)
    else:
        return jsonify({'message': 'no books found'})

@database_api.route('/update_book/<id>', methods=['PATCH', 'PUT'])
@token_required
def update_book(current_user_token, id):
    book = Book.query.filter_by(user_token = current_user_token.token, id=id).first()
    if book:
        temp_collection_status = request.json['collection_status']
        book.user_rating = request.json['user_rating']
        book.user_token = current_user_token.token
        if temp_collection_status == 'Completed' and book.collection_status != 'Completed':
            book.completed_date = datetime.utcnow()
        book.collection_status = temp_collection_status
        db.session.commit()
        output = book_schema.dump(book)
        print(output)
        return jsonify(output)
    else:
        return jsonify({'message': 'error'})

@database_api.route('/delete/<id>', methods=['DELETE'])
@token_required
def delete_book(current_user_token, id):
    book = Book.query.filter_by(user_token = current_user_token.token, id=id).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book has been successfully removed from your bin'})
    else:
        return jsonify({'message': 'A book with this ID was not found in your bin'})


@database_api.route('/update_profile', methods=['PATCH', 'PUT'])
@token_required
def update_profile(current_user_token):
    user = User.query.filter_by(token = current_user_token.token).first()

    if user:
        temp_name = request.json['name']
        temp_email = request.json['email']
        temp_password = request.json['password']
        if not temp_name or not temp_email or not temp_password or '@' not in temp_email:
            return jsonify({'message': 'invalid'})
        elif User.query.filter_by(email = temp_email).first() and current_user_token.email != temp_email:
            return jsonify({'message': 'email already in use'})
        else:
            user.name = temp_name
            user.email = temp_email       
            user.password = generate_password_hash(temp_password)
        db.session.commit()
        return jsonify({'message': 'profile updated successfully', 'email': user.email, 'name': user.name, 'password': temp_password})
        
@database_api.route('/get_count', methods=['GET', 'POST'])
@token_required
def get_count(current_user_token):
    all_count = 0
    completed_count = 0
    progress_count = 0
    future_count = 0
    all_books = Book.query.filter_by(user_token = current_user_token.token).all()
    for book in all_books:
        if book.collection_status == 'Completed':
            completed_count += 1
        elif book.collection_status == 'In progress':
            progress_count += 1
        else:
            future_count += 1
        all_count += 1

    print(all_count)
    print(completed_count)
    print(progress_count)
    print(future_count)
    
    return jsonify({'allCount': all_count, 'completedCount': completed_count, 'progressCount': progress_count, 'futureCount': future_count })
