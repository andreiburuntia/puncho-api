from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from app import db

class Weigh_In(db.Model):
    __tablename__ = 'weigh_ins'
    
    id = Column(Integer, primary_key=True)
    data = Column(String(200))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    def __init__(self, data, user_id):
        self.data = data
        self.user_id = user_id