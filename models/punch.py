from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from app import db

class Punch(db.Model):
    __tablename__ = 'punches'
    
    id = Column(Integer, primary_key=True)
    force = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    def __init__(self, force, user_id):
        self.force = force
        self.user_id = user_id