# coding: utf-8
from flask_sqlalchemy import SQLAlchemy

from extensions import db


class OneTimeInvestment(db.Model):
    __tablename__ = 'one_time_investment'
    __table_args__ = (
        db.CheckConstraint('processed IS FALSE OR value_after_fees IS NOT NULL AND stripe_payment_id IS NOT NULL'),
        {'schema': 'investment'}
    )

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    user = db.Column(db.ForeignKey('users.user_data.id'), nullable=False)
    value = db.Column(db.Double(53), nullable=False)
    processed = db.Column(db.Boolean, nullable=False, server_default=db.FetchedValue())
    stripe_payment_id = db.Column(db.String(50))
    time = db.Column(db.DateTime(True), nullable=False)
    value_after_fees = db.Column(db.Double(53))

    user_datum = db.relationship('UserDatum', primaryjoin='OneTimeInvestment.user == UserDatum.id',
                                 backref='one_time_investments')


class RecurringInvestment(db.Model):
    __tablename__ = 'recurring_investment'
    __table_args__ = (
        db.CheckConstraint('end_date IS NULL OR cancelled'),
        db.CheckConstraint(
            'processed IS FALSE OR value_after_fees IS NOT NULL AND stripe_subscription_id IS NOT NULL AND start_date IS NOT NULL'),
        {'schema': 'investment'}
    )

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    user = db.Column(db.ForeignKey('users.user_data.id'), nullable=False)
    value = db.Column(db.Double(53), nullable=False)
    processed = db.Column(db.Boolean, nullable=False, server_default=db.FetchedValue())
    stripe_subscription_id = db.Column(db.String(50))
    start_date = db.Column(db.DateTime(True), nullable=False)
    end_date = db.Column(db.DateTime(True))
    cancelled = db.Column(db.Boolean, nullable=False, server_default=db.FetchedValue())
    value_after_fees = db.Column(db.Double(53))

    user_datum = db.relationship('UserDatum', primaryjoin='RecurringInvestment.user == UserDatum.id',
                                 backref='recurring_investments')


class UserDatum(db.Model):
    __tablename__ = 'user_data'
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
