from sqlalchemy import Column, String, Integer, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship

import datetime

from app import db

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, default=datetime.datetime.utcnow)
    entries = Column(Integer)
    entries_left = Column(Integer)
    
    def __init__(self, user_id, start_time, end_time, entries, entries_left):
        self.user_id = user_id
        self.start_time = start_time
        self.end_time = end_time
        self.entries = entries
        self.entries_left = entries_left
