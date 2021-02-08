from sqlalchemy import Column, String, Integer, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship

import datetime

from app import db

class BulkPunch(db.Model):
    __tablename__ = 'bulkpunches'
    
    id = Column(Integer, primary_key=True)
    score = Column(Integer)
    count = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    workout_id = Column(Integer, ForeignKey('workouts.id'))

    def __init__(self, score, count, user_id, workout_id):
        self.score = score
        self.count = count
        self.user_id = user_id
        self.workout_id = workout_id