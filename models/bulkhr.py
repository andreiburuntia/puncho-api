from sqlalchemy import Column, String, Integer, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship

import datetime

from app import db

class BulkHr(db.Model):
    __tablename__ = 'bulkhrs'
    
    id = Column(Integer, primary_key=True)
    hr_min = Column(Integer)
    hr_max = Column(Integer)
    hr_avg = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    workout_id = Column(Integer, ForeignKey('workouts.id'))

    def __init__(self, hr_min, hr_max, hr_avg, user_id, workout_id):
        self.hr_min = hr_min
        self.hr_max = hr_max
        self.hr_avg = hr_avg
        self.user_id = user_id
        self.workout_id = workout_id