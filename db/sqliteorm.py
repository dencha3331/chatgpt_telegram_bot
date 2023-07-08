from datetime import datetime

from pony.orm import *

db = Database()


class Users(db.Entity):
    user_id = PrimaryKey(int)
    balance = Required(float)
    name = Required(str)
    surname = Required(str)
    age = Required(int)
    gender = Required(str)
    wish_news = Required(bool)
    reg_time = Required(datetime)


class Messages(db.Entity):
    user_id = Required(int)
    messages = Required(str)
    balance = Required(float)
    max_tokens = Required(int)


# db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
# db.generate_mapping(create_tables=True)
# s = Users(user_id=2828, tokens=123, name="den", surname="che", age=34, gender="male", wish_news=True,
#           reg_time=datetime.now())
# commit()
