'''Auth Flask app'''
import bcrypt
from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models.user import User # pylint: disable=unused-import
from database import db


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@localhost:3306/flask_auth'

login_manager = LoginManager()
db.init_app(app)


login_manager.init_app(app)
# view login
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    '''Load user'''
    return User.query.get(user_id)



@app.route('/login', methods=['POST'])
def login():
    '''Login route'''
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()
        check_password = bcrypt.checkpw(str.encode(password), str.encode(user.password))
        if user and check_password:
            login_user(user)
            # print(current_user)
            # print(current_user.is_authenticated)
            # print(current_user.username)
            return {'message': 'Logged in successfully!'}

    return jsonify({'message': 'Invalid credentials!'}), 400


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    '''Logout route'''
    logout_user()
    return {'message': 'Logged out successfully!'}


@app.route('/user', methods=['POST'])
def create_user():
    '''Create user route'''
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created successfully!'}
    return jsonify({'message': 'Invalid data!'}), 400


@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    '''Get user by ID route'''

    user = User.query.get(user_id)

    if user:
        return {'username': user.username, 'role': user.role}
    return jsonify({'message': f'User {user_id} not found!'}), 404


@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    '''Update user by ID route'''
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    user = User.query.get(user_id)

    if user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'You are not allowed to update other users!'}), 403
    if user and user_id != current_user.id and current_user.role == 'admin':
        if username:
            user.username = username
        if password:
            user.password = password
        if role:
            user.role = role
        db.session.commit()
        return {'message': f'User {user_id} updated successfully!'}
    if user and user_id == current_user.id:
        if password:
            user.password = password
        db.session.commit()
        return {'message': f'User {user_id} updated successfully!'}
    return jsonify({'message': f'User {user_id} not found!'}), 404


@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    '''Delete user by ID route'''
    if current_user.role != 'admin':
        return jsonify({'message': 'You are not allowed to delete other users!'}), 403
    if user_id == current_user.id:
        return jsonify({'message': 'You cannot delete yourself!'}), 403
    
    user = User.query.get(user_id)

    if user and user_id != current_user.id and current_user.role == 'admin':
        db.session.delete(user)
        db.session.commit()
        return {'message': f'User {user_id} deleted successfully!'}
    return jsonify({'message': f'User {user_id} not found!'}), 404


@app.route('/')
def hello_world():
    '''Hello World!'''
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
