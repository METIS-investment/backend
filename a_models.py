# coding: utf-8
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



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
