# coding: utf-8
from flask_sqlalchemy import SQLAlchemy


from extensions import db


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'users'}

    id = db.Column(db.String(40), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    second_name = db.Column(db.String(50), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False)
    registration_date = db.Column(db.DateTime(True), nullable=False)
    stripe_id = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    billable = db.Column(db.Boolean, nullable=False, server_default=db.FetchedValue())
    finish_signup = db.Column(db.Boolean, nullable=False, server_default=db.FetchedValue())
