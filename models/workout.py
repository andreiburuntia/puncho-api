from sqlalchemy import Column, String, Integer, Date, DateTime
from sqlalchemy.orm import relationship

import datetime

from app import db

class Workout(db.Model):
    __tablename__ = 'workouts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    description = Column(String(250))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, default=datetime.datetime.utcnow)
    w_type = Column(String(30))
    
    def __init__(self, name, description, start_time, end_time , w_type):
        self.name = name
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.w_type = w_type
