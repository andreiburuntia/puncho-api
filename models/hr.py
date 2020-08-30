from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

import datetime

from app import db

class Hr(db.Model):
    __tablename__ = 'hr'
    
    id = Column(Integer, primary_key=True)
    hr = Column(Integer)
    kcals = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __init__(self, hr, user_id, kcals, timestamp):
        self.hr = hr
        self.kcals = kcals
        self.user_id = user_id
        self.timestamp = timestamp