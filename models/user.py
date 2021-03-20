from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import relationship

from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    firstname = Column(String(30))
    lastname = Column(String(30))
    email = Column(String(30))
    birth_date = Column(String(30))
    address = Column(String(30))    
    gender = Column(String(30))
    nickname = Column(String(30))
    password_hash = Column(String(128))
    punches = relationship("Punch")
    
    def __init__(self, firstname, lastname, email, birth_date, address, gender, nickname, password_hash):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.birth_date = birth_date
        self.address = address
        self.gender = gender
        self.nickname = nickname
        self.password_hash = password_hash