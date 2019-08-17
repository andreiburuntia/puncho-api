from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from base import Base

class Punch(Base):
    __tablename__ = 'punches'
    
    id = Column(Integer, primary_key=True)
    force = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    def __init__(self, force):
        self.force = force