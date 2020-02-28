from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import relationship

from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(30))
    lastname = Column(String(30))
    email = Column(String(30))
    password_hash = Column(String(128))
    punches = relationship("Punch")
    
    def __init__(self, firstname, lastname, email, password_hash):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password_hash = password_hash
