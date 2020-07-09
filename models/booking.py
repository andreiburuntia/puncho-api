from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from app import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey('workouts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    def __init__(self, workout_id, user_id):
        self.workout_id = workout_id
        self.workout_id = user_id
