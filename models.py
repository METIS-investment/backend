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


class Company(db.Model):
    __tablename__ = 'company'
    __table_args__ = {'schema': 'companies'}

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    incorporation_date = db.Column(db.DateTime, nullable=False)



class Evaluation(db.Model):
    __tablename__ = 'evaluation'
    __table_args__ = {'schema': 'companies'}

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    company = db.Column(db.ForeignKey('companies.company.id'), nullable=False)
    profit = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Integer, nullable=False)
    assets = db.Column(db.Integer, nullable=False)
    liability = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    company1 = db.relationship('Company', primaryjoin='Evaluation.company == Company.id', backref='evaluations')



class Investment(db.Model):
    __tablename__ = 'investment'
    __table_args__ = {'schema': 'companies'}

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    amount = db.Column(db.Integer, nullable=False)
    share = db.Column(db.Double(53), nullable=False)
    company = db.Column(db.ForeignKey('companies.company.id'), nullable=False)

    company1 = db.relationship('Company', primaryjoin='Investment.company == Company.id', backref='investments')



class Profit(db.Model):
    __tablename__ = 'profit'
    __table_args__ = {'schema': 'companies'}

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
