import datetime

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Products(SqlAlchemyBase):
    __tablename__ = 'Products'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    seller = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey("users.id"))
    product = sqlalchemy.Column(sqlalchemy.String)
    weight = sqlalchemy.Column(sqlalchemy.Integer)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_sell = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    leader = orm.relation('User')
    """categories = orm.relation("Category",
                              secondary="association",
                              backref="jobs")"""
