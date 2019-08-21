from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import time

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@database-1.cluster-c4rbwipspsxn.us-east-2.rds.amazonaws.com/Test'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
#    os.path.join(basedir, 'test.db')
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

from models.user import User
from models.punch import Punch

# Base Schema
class Schema(ma.Schema):
    def __init__(self, strict=True, **kwargs):
        super(Schema, self).__init__(strict=True, **kwargs)

# User Schema
class UserSchema(Schema):
    class Meta:
        fields = ('id', 'firstname', 'lastname', 'email')

# Punch Schema
class PunchSchema(Schema):
    class Meta:
        fields = ('id', 'user_id', 'force')

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
punch_schema = PunchSchema()
punches_schema = PunchSchema(many=True)

# Create a User
@app.route('/user', methods=['POST'])
def add_user():
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']

    usr = User(firstname, lastname, email)
    
    db.session.add(usr)
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


bulk = []

# Add Punch
@app.route('/punch', methods=['POST'])
def add_punch():
    user_id = request.json['user_id']
    force = request.json['force']

    punch = Punch(force, user_id)

    global bulk

    bulk.append(punch)

    print(len(bulk))
    if len(bulk) > 10:
        db.session.add_all(bulk)
        bulk = []
        db.session.commit()

    return punch_schema.jsonify(punch)

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
