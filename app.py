from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_api import status
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
from models.hr import Hr
from models.weigh_in import Weigh_In
from models.workout import Workout
from models.booking import Booking

db.create_all()
db.session.commit()

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

# Hr Schema
class HrSchema(Schema):
    class Meta:
        fields = ('id', 'user_id', 'hr')

        
# Weigh_In Schema
class Weigh_InSchema(Schema):
    class Meta:
        fields = ('id', 'user_id', 'data')


# Workout Schema
class WorkoutSchema(Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'start_time')


# Workout Schema
class BookingSchema(Schema):
    class Meta:
        fields = ('id', 'workout_id', 'user_id')

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
punch_schema = PunchSchema()
punches_schema = PunchSchema(many=True)
hr_schema = HrSchema()
hrs_schema = HrSchema(many=True)
weigh_in_schema = Weigh_InSchema()
weigh_ins_schema = Weigh_InSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

# ------------ USER ----------------------

# Create a User
@app.route('/user', methods=['POST'])
def add_user():
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    password_hash = request.json['password_hash']

    usr = User(firstname, lastname, email, password_hash)

    found = False
    users = User.query.all()
    for u in users:
        if u.email == email:
            found = True
            break
    
    if found:
        return 'email registered already', status.HTTP_409_CONFLICT
    
    db.session.add(usr)
    db.session.commit()
    
    return user_schema.jsonify(usr), status.HTTP_201_CREATED

# Get All users
@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)

# Login
@app.route('/user/login', methods=['GET', 'POST'])
def login():
    email = request.json['email']
    password_hash = request.json['password_hash']
    user = {}
    users = User.query.all()
    for u in users:
        if u.email == email:
            user = u
            break
    if user == {}:
        return 'user not found', status.HTTP_401_UNAUTHORIZED
    else:
        if user.password_hash == password_hash:
            return user_schema.jsonify(user)
        else:
            return 'bad credentials', status.HTTP_401_UNAUTHORIZED

# Get user count
@app.route('/user/count', methods=['GET'])
def get_user_count():
    #users = User.query.all()
    users = db.session.query(User).all()
    user_count = len(users)
    print(user_count)
    return str(user_count)

# ------------ PUNCH ----------------------


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

# Get Punches for specific User
@app.route('/punch/<user_id>', methods=['GET'])
def get_punches_for_user(user_id):
    qry =  Punch.query.filter(Punch.user_id == user_id).all()
    #print(qry)
    return punches_schema.jsonify(qry)

# Get Punch Score
@app.route('/punch/score/<user_id>', methods=['GET'])
def get_punch_score_for_user(user_id):
    qry =  Punch.query.join(User).filter(User.id == user_id)
    #print(qry)
    return "1000"

# ------------ HR ---------------

# Add Hr
@app.route('/hr', methods=['POST'])
def add_hr():
    user_id = request.json['user_id']
    rate = request.json['hr']

    hr = Hr(rate, user_id)

    global bulk

    bulk.append(hr)

    print(len(bulk))
    if len(bulk) > 10:
        db.session.add_all(bulk)
        bulk = [] 
        db.session.commit()

    return punch_schema.jsonify(hr)

# Get Latest Hr
@app.route('/hr/latest/<user_id>', methods=['GET'])
def get_latest_hr_for_user(user_id):
    qry =  Hr.query.filter(Hr.user_id == user_id)
    # return last in collection
    #print(qry)
    return '{"hr": "100", "kcals": "22"}'

# Get Avg Hr
@app.route('/hr/avg/<user_id>', methods=['GET'])
def get_avg_hr_for_user(user_id):
    qry =  Hr.query.filter(Hr.user_id == user_id)
    # return avg in collection
    #print(qry)
    return "99"


# ---------- WEIGH IN -------------

# Add weigh in
@app.route('/weigh_in', methods=['POST'])
def add_weigh_in():
    user_id = request.json['user_id']
    data = request.json['data']

    w = Weigh_In(data, user_id)

    db.session.add(w)
    db.session.commit()

    return weigh_in_schema.jsonify(w)

# Get weigh ins
@app.route('/weigh_in/<user_id>', methods=['GET'])
def get_weigh_ins(user_id):
    qry =  Weigh_In.query.filter(Weigh_In.user_id == user_id).all()
    # return last in collection
    #print(qry)
    return weigh_ins_schema.jsonify(qry)


# --------- WORKOUTS ------------

# Add Workout
@app.route('/workout', methods=['POST'])
def add_workout():
    description = request.json['description']
    name = request.json['name']
    start_time = request.json['start_time']

    w = Workout(description, name, start_time)

    db.session.add(w)
    db.session.commit()

    return workout_schema.jsonify(w)

# Get Workouts
@app.route('/workout', methods=['GET'])
def get_wourkouts():
    qry =  Workout.query.all()
    #print(qry)
    return workouts_schema.jsonify(qry)

# Get Workout Summary
@app.route('/workout/summary', methods=['GET'])
def get_workout_summary():
    user_id = request.json['user_id']
    workout_id = request.json['workout_id']
    qry =  Hr.query.filter(Hr.user_id == user_id)
    # return avg in collection
    #print(qry)
    return '{"avg_hr": "101", "max_hr": "149", "kcals": "774", "punch_score": "99912"}'


# ---------- BOOKINGS ------------

# Add Booking
@app.route('/booking', methods=['POST'])
def add_booking():
    workout_id = request.json['workout_id']
    user_id = request.json['user_id']

    b = Booking(workout_id, user_id)
    print(workout_id, user_id)
    print(booking_schema.jsonify(b))
    db.session.add(b)
    db.session.commit()

    return booking_schema.jsonify(b)

# Get Bookings for User
@app.route('/booking/<user_id>', methods=['GET'])
def get_bookings_for_user(user_id):
    qry =  Booking.query.filter(Booking.user_id==user_id).all()
    # return last in collection
    #print(qry)
    return bookings_schema.jsonify(qry)


# ------------------ DOCS ----------------

@app.route('/docs', methods=['GET'])
def get_docs():
    script_dir = os.path.dirname(__file__)
    rel_path = "api-docs/puncho-api.html"
    abs_file_path = os.path.join(script_dir, rel_path)
    f = open(abs_file_path)
    return f.read()

# ------------------ WEB ----------------

@app.route('/web', methods=['GET'])
def get_web():
    return render_template('Home_After.html')


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
