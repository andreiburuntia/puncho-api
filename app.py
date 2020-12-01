from flask import Flask, request, jsonify, send_from_directory, render_template, Response, redirect, url_for, session
from flask_table import Table, Col
from flask_api import status
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length
from flask import render_template, flash, redirect
from dateutil.relativedelta import relativedelta
import os
import time
import json
import datetime
import random
import platform
import sys
import jwt #pip install PyJWT
import requests
import json
from Crypto.PublicKey.RSA import construct, importKey #pip install pycrypto
import base64 #pip install pybase64
import stripe

stripe.api_key = 'sk_test_51HYErVLvvkhUISt4TYOB2XO9dtI7ocsGYfUC3ZqtX7AtCOv2ufgB3jP5HSwrIzrUyEJeN7UghxNz5pJgoDKOmTbv002rcrojTz'

# Init app
app = Flask(__name__)
cors = CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@database-1.cluster-c4rbwipspsxn.us-east-2.rds.amazonaws.com/Test'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
#    os.path.join(basedir, 'test.db')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
 
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
from models.subscription import Subscription

db.create_all()
db.session.commit()

stripe_keys = {
  'secret_key': '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',
  'publishable_key': 'pk_live_51HYErVLvvkhUISt4raKM3DN0JvpI6au5jEfr3lk1kAw8BXyEru9upMyVmJSYSqcf8NcF8xrggJ61LvXv1NOFXC9P007KnDc0bE'
}

stripe.api_key = stripe_keys['secret_key']


# Base Schema
class Schema(ma.Schema):
    def __init__(self, strict=True, **kwargs):
        super(Schema, self).__init__(strict=True, **kwargs)

# User Schema
class UserSchema(Schema):
    class Meta:
        fields = ('id', 'firstname', 'lastname', 'email', 'birth_date', 'address', 'gender', 'nickname')

# Punch Schema
class PunchSchema(Schema):
    class Meta:
        fields = ('id', 'user_id', 'score', 'count')

# Hr Schema
class HrSchema(Schema):
    class Meta:
        fields = ('id', 'user_id', 'hr', 'kcals')

        
# Weigh_In Schema
class Weigh_InSchema(Schema):
    class Meta:
        fields = ('id', 'user_id', 'data')


# Workout Schema
class WorkoutSchema(Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'start_time', 'end_time', 'w_type', 'rounds', 'rest_time', 'trainer')


# Booking Schema
class BookingSchema(Schema):
    class Meta:
        fields = ('id', 'workout_id', 'user_id')

# Subscription Schema
class SubscriptionSchema(Schema):
    class Meta:
        fields = ('id', 'user_id', 'start_time', 'end_time', 'entries', 'entries_left')

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
subscription_schema = SubscriptionSchema()
subscriptions_schema = SubscriptionSchema(many=True)

# BAG - USER ID MAP
bag_map = {
    "001": "",
    "002": "",
    "003": "",
    "004": "",
    "005": "",
    "006": "",
    "007": "",
    "008": "",
    "009": "",
    "010": "",
    "011": "",
    "012": "",
    "013": "",
    "014": "",
    "015": "",
    "016": "",
    "017": "",
    "018": "",
    "019": "",
    "020": ""    
}

def clear_bag_map():
    for key in bag_map:
        bag_map[key]=""
        
def remove_user_from_bag_map(user_id):
    for key in bag_map:
        if bag_map[key] == user_id:
            bag_map[key] = ""
            
used_bags = []

# ----------- STRIPE ----------

@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 500

    customer = stripe.Customer.create(
        email='customer@example.com',
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

    return 'ok', status.HTTP_200_OK

# ------------ USER ----------------------

# Create a User
@app.route('/user', methods=['POST'])
def add_user():
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    email = request.json['email']
    birth_date = request.json['birth_date']
    address = request.json['address']
    gender = request.json['gender']
    nickname = request.json['nickname']
    password_hash = request.json['password_hash']

    usr = User(firstname, lastname, email, birth_date, address, gender, nickname, password_hash)

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
@app.route('/user/login', methods=['POST'])
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

# Apple sign in

@app.route('/user/login/apple-sign-in', methods=['POST'])
# DONE copy decoder.py DONE
def apple_sign_in_clinet():
    obj = request.json

    marius_jwt = 'eyJraWQiOiJCRkpRUFY2WEdYIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJDUVJRNTVVSzZWIiwiaWF0IjoxNjAxNzM4Njg5LCJleHAiOjE2MTcyOTA2ODksImF1ZCI6Imh0dHBzOi8vYXBwbGVpZC5hcHBsZS5jb20iLCJzdWIiOiJjb20ubGVnZW5kLmJveGluZyJ9.u2Uu_-fHajZetQnkV69b6k6tUiz3-G-iHNlBGZLc_BpsYL0gTe4mnWLO1GDPLNglvTvx6iPbGHdwXwq3yVR5-w'


    email = obj['email']
    authorizationCode = obj['authorizationCode']
    identityToken= obj['identityToken']
    firstname = obj['fullName']['givenName']
    lastname = obj['fullName']['familyName']
    email = obj['user']

    print(obj)

    print('fetching keys...')

    r = requests.get('https://appleid.apple.com/auth/keys')
    n_decoded = ''
    e_decoded = ''
    alg = ''
    decoded = ''

    for key in r.json()['keys']:
        try:
            n = key['n'] + '=='
            n_decoded = base64.urlsafe_b64decode(n)
            n_decoded = int.from_bytes(n_decoded, 'big')
            e = key['e'] + '=='
            e_decoded = base64.urlsafe_b64decode(e)
            e_decoded = int.from_bytes(e_decoded, 'big')
            alg = key['alg']
            key = construct((n_decoded, e_decoded))
            keyPub = key.exportKey(format='PEM')
            decoded = jwt.decode(identityToken, keyPub, algorithms=alg, audience='com.legend.boxing')
            print(decoded)
        except:
            pass
    
    class O:
        pass

    o = O()
    o.client_id = 'com.legend.boxing'
    o.client_secret = marius_jwt
    o.code = authorizationCode
    o.grant_type = 'authorization_code'

    data = o.__dict__
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    r = requests.post('https://appleid.apple.com/auth/token', data, headers)
    res_obj = r.json()

    print(res_obj)

    if 'error' in res_obj:
        return res_obj['error'], status.HTTP_401_UNAUTHORIZED

    # DEBUG - remove this
    print(email)


    user = {}
    users = User.query.all()
    for u in users:
        if u.email == email:
            user = u
            break
    if user == {}:
        user = User(firstname, lastname, email, '', '', '', 'apple')
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user), status.HTTP_201_CREATED
    else:     
        return user_schema.jsonify(user)

marius_jwt = 'eyJraWQiOiJCRkpRUFY2WEdYIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJDUVJRNTVVSzZWIiwiaWF0IjoxNjAxNzI5NTc2LCJleHAiOjE2MTcyODE1NzYsImF1ZCI6Imh0dHBzOi8vYXBwbGVpZC5hcHBsZS5jb20iLCJzdWIiOiJjb20ubGVnZW5kLmJveGluZy5jbGllbnQifQ.GNBAyLgtQ3eO4fJiqjeoIB7iQMlbTzpG1FOdjA5nwTfZJ8NMNlKnjbjVqKKfWrovx4_r6o-h8bTtP2NfPQGYLQ'

@app.route('/user/login/apple', methods=['POST'])
def apple_login():
    print(request)
    return 'ok'

# Get user details
@app.route('/user/details/<user_id>', methods=['GET'])
def get_details(user_id):
    user_id = user_id
    user = User.query.get(int(user_id))
    user.password_hash = 'hidden'
    return user_schema.jsonify(user)

# Get user details by email
@app.route('/user/details_by_email/<email>', methods=['GET'])
def get_details_by_email(email):
    user = User.query.filter(User.email == email).order_by(User.id.desc()).first()
    return user_schema.jsonify(user)

# Get user count
@app.route('/user/count', methods=['GET'])
def get_user_count():
    #users = User.query.all()
    users = db.session.query(User).all()
    user_count = len(users)
    print(user_count)
    return str(user_count)

# Update user
@app.route('/user/update', methods=['POST'])
def update_user_details():
    user_id = request.json['id']
    #firstname = request.json['firstname']
    #lastname = request.json['lastname']
    #email = request.json['email']
    birth_date = request.json['birth_date']
    address = request.json['address']
    gender = request.json['gender']
    nickname = request.json['nickname']
    
    user = User.query.get(int(user_id))
    #user.firstname = firstname
    #user.lastname = lastname
    #user.email = email
    user.birth_date = birth_date
    user.address = address
    user.gender = gender
    user.nickname = nickname

    db.session.commit()

    return user_schema.jsonify(user)

# Get User Stats
@app.route('/user/stats/<user_id>', methods=['GET'])
def user_stats(user_id):
    user = User.query.get(int(user_id))
    obj = json.loads('{ "score" : 578, "punches" : { "total" : 1763, "perSecond": 6.3 }, "force" : { "perPunch": 11.3 }, "rank": 20, "workouts": 52, "classes" : 33, "calories": 3471, "trained" : { "hours" : 12, "minutes": 45 } }')

    return json.dumps(obj), status.HTTP_200_OK


# ------------ PUNCH ----------------------


bulk = []

# Add Punch
@app.route('/punch', methods=['POST'])
def add_punch():
    bag_id = request.json['bag_id']
    score = request.json['score']
    count = request.json['count']

    if bag_map[bag_id] == "":
        return "no user registered to this bag: " + bag_id

    user_id = bag_map[bag_id]

    punch = Punch(score, count, user_id, datetime.datetime.now())

    db.session.add(punch)
    db.session.commit()

    #global bulk

    #bulk.append(punch)

    #print(len(bulk))
    #if len(bulk) > 10:
    #    db.session.add_all(bulk)
    #    bulk = [] 
    #    db.session.commit()

    return punch_schema.jsonify(punch)

# Get Punches for specific User
@app.route('/punch/<user_id>', methods=['GET'])
def get_punches_for_user(user_id):
    qry =  Punch.query.filter(Punch.user_id == user_id).all()
    
    return punches_schema.jsonify(qry)

# Get Punch Score
@app.route('/punch/latest/<user_id>', methods=['GET'])
def get_punch_score_for_user(user_id):
    qry =  Punch.query.filter(Punch.user_id == user_id).order_by(Punch.id.desc()).first()
    
    return punch_schema.jsonify(qry)

# Get Punch Score and HR data
@app.route('/punch/latest-with-hr/<user_id>', methods=['GET'])
def get_punch_score_with_hr_for_user(user_id):
    p_qry =  Punch.query.filter(Punch.user_id == user_id).order_by(Punch.id.desc()).first()
    hr_qry = Hr.query.filter(Hr.user_id == user_id).order_by(Hr.id.desc()).first()
    
    p_dict = json.loads(punch_schema.dumps(p_qry)[0])
    hr_dict = json.loads(hr_schema.dumps(hr_qry)[0])
    
    res = {**p_dict, **hr_dict}
    
    res_json = json.dumps(res)
    
    return jsonify(res)

# ------------ HR ---------------

# Add Hr
@app.route('/hr', methods=['POST'])
def add_hr():
    bag_id = request.json['bag_id']
    rate = request.json['hr']

    if bag_map[bag_id] == "":
        return "no user registered to this bag: " + bag_id

    user_id = bag_map[bag_id]

    hr = Hr(rate, user_id, "0", datetime.datetime.now())

    db.session.add(hr)
    db.session.commit()

    #global bulk

    #bulk.append(hr)

    #print(len(bulk))
    #if len(bulk) > 10:
    #    db.session.add_all(bulk)DateTime
    #    bulk = [] 
    #    db.session.commit()

    return hr_schema.jsonify(hr)

# Get Latest Hr
@app.route('/hr/latest/<user_id>', methods=['GET'])
def get_latest_hr_for_user(user_id):
    qry =  Hr.query.filter(Hr.user_id == user_id).order_by(Hr.id.desc()).first()
    # return last in collection
    # COMPUTE KCAL!?
    return hr_schema.jsonify(qry)

# Get Avg Hr
@app.route('/hr/avg/<user_id>', methods=['GET'])
def get_avg_hr_for_user(user_id):
    time_1h_ago = datetime.datetime.now() - datetime.timedelta(hours=1.5)
    qry =  Hr.query.filter(Hr.user_id == user_id, Hr.timestamp > time_1h_ago).order_by(Hr.id.desc())
    sum = 0
    cnt = 0
    max = 0
    for h in qry:
        sum = sum + h.hr
        cnt = cnt + 1
        if max < h.hr:
            max = h.hr
    avg = sum/cnt
    # return avg in collection
    #print(qry)
    return jsonify({'avg': avg, 'max': max, 'kcals': 1991})


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
    end_time = request.json['end_time']
    w_type = request.json['w_type']
    rounds = request.json['rounds']
    rest_time = request.json['rest_time']
    trainer = request.json['trainer']

    w = Workout(description, name, start_time, end_time, w_type, rounds, rest_time, trainer)

    db.session.add(w)
    db.session.commit()

    return workout_schema.jsonify(w)

# Get Workouts
@app.route('/workout', methods=['GET'])
def get_wourkouts():
    qry =  Workout.query.all()
    #print(qry)
    return workouts_schema.jsonify(qry)

# DONE some day's workouts - ca la upcoming - params: date
# Get Some Day's Workouts
@app.route('/workout/day/<date>', methods=['GET'])
def get_day_workout(date):
    t1 = datetime.datetime.strptime(date, '%Y-%m-%d')
    print(t1)
    t2 = datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(days=1)
    print(t2)
    qry = Workout.query.filter(Workout.start_time >= t1, Workout.start_time <= t2).order_by(Workout.start_time.asc()).all()
    return workouts_schema.jsonify(qry)

# Get Workout Details by Id
@app.route('/workout/details/<workout_id>', methods=['GET'])
def get_workout_details(workout_id):
    qry = Workout.query.filter(Workout.id == workout_id).first()
    return workout_schema.jsonify(qry)

# Get Upcoming Workout
@app.route('/workout/upcoming', methods=['GET'])
def get_upcoming_workout():
    qry = Workout.query.filter(Workout.start_time > datetime.datetime.now()).order_by(Workout.id.asc()).first()
    return workout_schema.jsonify(qry)

# Get Workout Summary
@app.route('/workout/summary', methods=['GET'])
def get_workout_summary():
    user_id = request.args.get('user_id')
    workout_id = request.args.get('workout_id')
    
    w_qry= Workout.query.filter(Workout.id == workout_id).first()
    
    w_start_time = w_qry.start_time
    print(w_start_time)
    w_end_time = w_qry.end_time
    print(w_end_time)
    
    p_qry = Punch.query.filter(Punch.user_id == user_id, Punch.timestamp > w_start_time, Punch.timestamp < w_end_time).order_by(Punch.id.desc()).first()
    #print(punch_schema.jsonify(p_qry))
    hr_qry =  Hr.query.filter(Hr.user_id == user_id, Hr.timestamp > w_start_time, Hr.timestamp < w_end_time).order_by(Hr.id.desc())
    #print(hr_schema.jsonify(hr_qry))
    sum = 0
    cnt = 1
    max = 0
    for h in hr_qry:
        sum = sum + h.hr
        cnt = cnt + 1
        if max < h.hr:
            max = h.hr
    avg = sum/cnt
    
    if p_qry is not None:
        p_score = p_qry.score
        p_count = p_qry.count
    else:
        p_score = 0
        p_count = 0

    w_name = w_qry.name
    w_type = w_qry.w_type
       
    #return jsonify({'name': w_name, 'start_time': w_start_time, 'end_time': w_end_time, 'type': w_type, "avg_hr": avg, 'max_hr': max, 'kcals': 741, 'punch_score': p_score, 'punch_count': p_count})
    return jsonify({'name': w_name, 'start_time': w_start_time, 'end_time': w_end_time, 'type': 'BOX', "avg_hr": 134, 'max_hr': 167, 'kcals': 741, 'punch_score': 1974, 'punch_count': 364})


# ---------- BOOKINGS ------------

# Add Booking
@app.route('/booking', methods=['POST'])
def add_booking():
    workout_id = request.json['workout_id']
    user_id = request.json['user_id']

    try:
        user_bookings =  Booking.query.filter(Booking.user_id==user_id).all()
        for b in user_bookings:
            if int(b.workout_id) == int(workout_id):
                return Response("{'error': 'Already registered.'}", status=409, mimetype='application/json')
    except:
        pass

    sub = Subscription.query.filter(Subscription.user_id == user_id, Subscription.start_time < datetime.datetime.now(), Subscription.end_time > datetime.datetime.now()).order_by(Subscription.id.desc()).first()
    try:
        entries_left = sub.entries_left
        if entries_left > 0:
            bookings = Booking.query.filter(Booking.workout_id == workout_id).all()
            if len(bookings) < 20:
                b = Booking(workout_id, user_id)

                sub.entries_left -= 1

                db.session.add(b)
                db.session.commit()

                return booking_schema.jsonify(b)
            else:
                return Response("{'error': 'Workout is full.'}", status=409, mimetype='application/json')
        else:
            return Response("{'error': 'Out of entry tokens.'}", status=409, mimetype='application/json')
    except:
        return Response("{'error': 'No subscription.'}", status=409, mimetype='application/json')

# Get Bookings for User
@app.route('/booking/<user_id>', methods=['GET'])
def get_bookings_for_user(user_id):
    qry =  Booking.query.filter(Booking.user_id==user_id).all()
    # return last in collection
    #print(qry)
    return bookings_schema.jsonify(qry)

# Remove Booking
@app.route('/booking/remove', methods=['POST'])
def remove_booking():
    workout_id = request.json['workout_id']
    user_id = request.json['user_id']

    Booking.query.filter(Booking.workout_id == workout_id, Booking.user_id == user_id).delete()
    sub = Subscription.query.filter(Subscription.user_id == user_id, Subscription.start_time < datetime.datetime.now(), Subscription.end_time > datetime.datetime.now()).order_by(Subscription.id.desc()).first()
    
    sub.entries_left += 1 
    db.session.commit()

    return Response("{'ok': 'ok'}", status=200, mimetype='application/json')

# ------------- BAG LINK ---------------

# Link Bag
@app.route('/link_bag', methods=['POST'])
def link_bag():
    user_id = request.json['user_id']
    bag_id = request.json['bag_id']
    
    if bag_id not in bag_map.keys():
        return json.dumps({'success':False}), 409, {'ContentType':'application/json'}
    
    if bag_id in used_bags:
        return json.dumps({'success':False}), 409, {'ContentType':'application/json'}
    
    used_bags.append(bag_id)
    bag_map[bag_id] = user_id
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    
# ----------- END SESSION ------------
@app.route('/end_session', methods=['POST'])
def end_session():
    user_id = request.json['user_id']
    bag_id = request.json['bag_id']
    
    try:
        remove_user_from_bag_map(user_id)
        used_bags.remove(bag_id)
    except:
        print('FAIL')

    w_qry = Workout.query.filter(Workout.start_time < datetime.datetime.now()).order_by(Workout.start_time.desc()).first()
    
    return workout_schema.jsonify(w_qry)

# ----------- SUBSCRIPTION -----------
@app.route('/subscription', methods=['POST'])
def add_subscription():
    user_id = request.json['user_id']
    start_time = request.json['start_time']
    end_time = request.json['end_time']
    entries = request.json['entries']
    entries_left = entries

    new_sub = Subscription(user_id, start_time, end_time, entries, entries_left)

    db.session.add(new_sub)
    db.session.commit()

    return subscription_schema.jsonify(new_sub)

@app.route('/subscription/<user_id>', methods=['GET'])
def get_user_subscriptiono(user_id):
    sub = Subscription.query.filter(Subscription.user_id == user_id, Subscription.start_time < datetime.datetime.now(), Subscription.end_time > datetime.datetime.now()).order_by(Subscription.id.desc()).first()
    return subscription_schema.jsonify(sub)

# DUMMY DEMO
r = 0
dummy_score = [0] * 21
dummy_count = [0] * 21

# DUMMY DEMO END

# ----------- PROIECTOR ---------------
@app.route('/proiector', methods=['GET'])
def proiector():
    obj_list = []

    for i in range(20):
        obj = {}    
        obj['bag_id'] = i + 1
        obj['count'] = 0
        obj['score'] = 0
        obj['hr'] = 0
        obj['effort'] = 1 # 1 to 3
        offset = '0'
        if i<9:
            offset = '00'
        #print(offset + str(obj['bag_id']))
        if offset + str(obj['bag_id']) in used_bags:
            #print(obj['bag_id'])
            usr = bag_map[offset + str(obj['bag_id'])]
            user_id = usr
            try:
                p_qry =  Punch.query.filter(Punch.user_id == user_id).order_by(Punch.id.desc()).first()
                obj['count'] = p_qry.count
                obj['score'] = p_qry.score
            except:
                obj['count'] = 0
                obj['score'] = 0
            try:
                hr_qry =  Hr.query.filter(Hr.user_id == user_id).order_by(Hr.id.desc()).first()
                obj['hr'] = hr_qry.hr
            except:                
                obj['hr'] = 0
            
        obj_list.append(obj)
    
    # DUMMY DEMO

    #if dummy_score[1] > 3000:
    #    dummy_count = [0] * 21
    #    dummy_score = [0] * 21

    #obj_list = []
    #for i in range(1, 21):
    #    obj = {}
    #
    #    obj['bag_id'] = i
    #
    #    dummy_score[i] += random.randint(7, 13)
    #    obj['score'] = dummy_score[i]
    #
    #    dummy_count[i] += random.randint(1, 5)/5
    #    obj['count'] = int(dummy_count[i])
    #
    #    obj['hr'] = random.randint(120, 135)
    #    obj_list.append(obj)

    # DUMMY DEMO END

    return str(obj_list)


# ---------- RECEPTIE ---------------

class CustomerTable(Table):
    firstname = Col('First Name')
    lastname = Col('Last Name')
    email = Col('Email')
    uid = Col('ID')
    dummy = Col('dummy')

class WorkoutTable(Table):
    name = Col('Name')
    w_type = Col('Type')
    start_time = Col('Start Time')

@app.route('/office/upcoming-info')
def upcoming_info():
    w_qry = Workout.query.filter(Workout.start_time > datetime.datetime.now()).order_by(Workout.id.asc()).first()
    w_id = w_qry.id

    b_qry =  Booking.query.filter(Booking.workout_id==w_id).all()

    users = []
    for b in b_qry:
        u_id = b.user_id
        user = User.query.get(int(u_id))
        users.append(user)

    item_list = []
    cnt = 0
    for i in users:
        cnt += 1
        item_list.append(dict(firstname=i.firstname, lastname=i.lastname, email=i.email, uid=i.id, dummy='replaceMe'))
    table = CustomerTable(item_list)
    class_info = w_qry.name + ' - ' + w_qry.w_type + ' - ' + str(w_qry.start_time)
    return render_template('upcoming_info.html',
                           class_info=class_info,
                           workout_id=w_id,
                           dyn_table=table,)

class SubscriptionForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    start_date = DateField('Start Date (dd/mm/yyyy - e.g. 21/08/2020', format='%d/%m/%Y', validators=[DataRequired()])
    entries = SelectField('Entries', choices = ['1', '8', '12', '999'], validators = [DataRequired()])
    submit = SubmitField('Add Subscription')

@app.route('/office/subscription', methods=['GET', 'POST'])
def office_sub():
    form = SubscriptionForm()
    if request.method == 'POST':
        try:
            start_date = datetime.datetime.strptime(request.form.get('start_date'), '%d/%m/%Y')
            email = request.form.get('email')
            entries = request.form.get('entries')

            usr = User.query.filter(User.email == email).order_by(User.id.desc()).first()
            user_id = usr.id

            entries_left = entries

            end_time = start_date + relativedelta(months=1)
            start_time = start_date

            new_sub = Subscription(user_id, start_time, end_time, entries, entries_left)

            db.session.add(new_sub)
            db.session.commit()

            #return subscription_schema.jsonify(new_sub)

        except:
            print('failed')
        
    return render_template('subscription.html', form=form)

# ------------ PAYMENTS -----------------

YOUR_DOMAIN = 'http://ec2-18-217-1-165.us-east-2.compute.amazonaws.com/checkout'

@app.route('/create-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': 2000,
                        'product_data': {
                            'name': 'Stubborn Attachments',
                            'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '?success=true',
            cancel_url=YOUR_DOMAIN + '?canceled=true',
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/pay', methods=['POST'])
def pay():
    data = request.get_json()
    intent = None

    try:
        if 'payment_method_id' in data:
            # Create the PaymentIntent
            intent = stripe.PaymentIntent.create(
                payment_method=data['payment_method_id'],
                amount=1099,
                currency='ron',
                confirmation_method='manual',
                confirm=True,
            )
        elif 'payment_intent_id' in data:
            intent = stripe.PaymentIntent.confirm(data['payment_intent_id'])
    except stripe.error.CardError as e:
    # Display error on client
        return json.dumps({'error': e.user_message}), 200

    return generate_response(intent)


def generate_response(intent):
    # Note that if your API version is before 2019-02-11, 'requires_action'
    # appears as 'requires_source_action'.
    if intent.status == 'requires_action' and intent.next_action.type == 'use_stripe_sdk':
    # Tell the client to handle the action
        return json.dumps({
            'requires_action': True,
            'payment_intent_client_secret': intent.client_secret,
        }), 200
    elif intent.status == 'succeeded':
        # The payment didn’t need any additional actions and completed!
        # Handle post-payment fulfillment
        return json.dumps({'success': True}), 200
    else:
        # Invalid status
        return json.dumps({'error': 'Invalid PaymentIntent status'}), 500

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
