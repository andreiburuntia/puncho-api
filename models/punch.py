from sqlalchemy import Column, String, Integer, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship

import datetime

from app import db

class Punch(db.Model):
    __tablename__ = 'punches'
    
    id = Column(Integer, primary_key=True)
    score = Column(Integer)
    count = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self, score, count, user_id, timestamp):
        self.score = score
        self.count = count
        self.user_id = user_id
        self.timestamp = timestamp