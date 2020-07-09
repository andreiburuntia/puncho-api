from sqlalchemy import Column, String, Integer, Date, DateTime
from sqlalchemy.orm import relationship

import datetime

from app import db

class Workout(db.Model):
    __tablename__ = 'workouts'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    name = Column(String(30))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self, name, description, start_time, end_time):
        self.name = name
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
