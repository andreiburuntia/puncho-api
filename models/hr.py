from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from app import db

class Hr(db.Model):
    __tablename__ = 'hr'
    
    id = Column(Integer, primary_key=True)
    hr = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    def __init__(self, hr, user_id):
        self.hr = hr
        self.user_id = user_id