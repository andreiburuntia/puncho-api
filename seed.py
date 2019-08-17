from datetime import date

from models.user import User
from base import Session, engine, Base
from models.punch import Punch

Base.metadata.create_all(engine)

session = Session()

user1 = User('User', 'One', 'userone@mail.com')
user2 = User('User', 'Two', 'usertwo@gmail.com')

punch1 = Punch(1)
punch2 = Punch(2)

user1.punches.append(punch1)
user1.punches.append(punch2)

user2.punches.append(punch1)

session.add(user1)
session.add(punch1)

session.commit()

for i in range(300):
    print(i)
    session.add(User(str(i), 'asd', 'asd'))


session.commit()
users = session.query(User).join(Punch).all()
print(len(users))