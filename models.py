__author__ = 'nahla.errakik'

import datetime
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

login = LoginManager()
db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(256))
    email = db.Column(db.String(50), unique=True)

    def get_user(self, email):
        record = User.query.filter(User.email == email).first()
        if record:
            return User(id=record.id, username=record.username, password=record.password, email=record.email)
        return None

    def add_user(self, username, password, email):
        new_record = User(username=username, password=password, email=email)
        db.session.add(new_record)
        db.session.commit()

    def check_password(self, password):
        return self.password == password

    def __str__(self):
        return '<User %r, %s, %s>' % (self.id, self.username, self.email)


class Search(db.Model):
    __tablename__ = "Search"

    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.datetime.now)
    keyword = db.Column(db.String(256))
    text = db.Column(db.String())

    def search(self, keyword):
        result = []
        #records = Search.query.filter(Search.keyword == keyword).distinct().order_by(desc(Search.creation_time))
        records = Search.query.filter_by(keyword=keyword).distinct(Search.text).order_by(desc(Search.creation_time))
        '''select dinstinct * from Search where keyword=keyword order by creation_time'''
        for record in records:
            item = Search(id=record.id, creation_time=record.creation_time, keyword=record.keyword, text=record.text)
            result.append(item)

        return result

    def add_search(self, search_item):
        db.session.add(search_item)
        db.session.commit()

    @staticmethod
    def less_than_5minutes(start):
        time_now = datetime.datetime.now()
        # db_time = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S.%f')
        time_delta = (time_now - start)
        diff_in_min = time_delta.total_seconds() / 60

        if diff_in_min < 5:
            return True
        else:
            return False


class Tweet(db.Model):
    __tablename__ = "Tweet"

    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.datetime.now)
    keyword = db.Column(db.String(256))
    text = db.Column(db.String())
    user = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)


@login.user_loader
def load_user(email):
    return User.query.get(email)
