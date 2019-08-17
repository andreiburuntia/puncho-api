from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from models.user import User
import time

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@database-1.cluster-c4rbwipspsxn.us-east-2.rds.amazonaws.com/Test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'firstname', 'lastname', 'email')


# Init schema
user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)

bulk = []

# Create a User
@app.route('/user', methods=['POST'])
def add_user():
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']

    usr = User(firstname, lastname, email)

    global bulk

    bulk.append(usr)

    print(len(bulk))
    if len(bulk) > 10:
        db.session.add_all(bulk)
        bulk = []
        db.session.commit()

    return user_schema.jsonify(usr)

# Get All users
@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)

# Get Single users
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

# Update a user
@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)

    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']

    user.firstname = firstname
    user.lastname = lastname
    user.email = email

    db.session.commit()

    return user_schema.jsonify(user)

# Delete user
@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)

# Get user count
@app.route('/user/count', methods=['GET'])
def get_user_count():
    #users = User.query.all()
    users = db.session.query(User).all()
    user_count = len(users)
    print(user_count)
    return str(user_count)

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
