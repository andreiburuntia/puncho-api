from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from app import db

class Punch(db.Model):
    __tablename__ = 'punches'
    
    id = Column(Integer, primary_key=True)
    score = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    def __init__(self, score, user_id):
        self.score = score
        self.user_id = user_id