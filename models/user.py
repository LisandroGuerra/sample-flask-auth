'''User model for database'''
from flask_login import UserMixin
from database import db


class User(db.Model, UserMixin):
    '''User model for database'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
