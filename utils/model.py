import datetime

from utils.db_utils import Base
from sqlalchemy import Column, String, BigInteger, Boolean, DateTime, SmallInteger, LargeBinary


class User(Base):
    __tablename__ = "usr"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, index=True)
    user_name = Column(String)
    first_name = Column(String)
    isPrivilege = Column(Boolean, default=False)
    number_curse = Column(SmallInteger)
    isBanned = Column(Boolean, default=False)
    isBannedMessage = Column(Boolean, default=False)
    date_registration = Column(DateTime, default=datetime.datetime.utcnow())


class Last_Action(Base):
    __tablename__ = 'last_action'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, index=True)
    action = Column(String)
    date_registration = Column(DateTime, default=datetime.datetime.utcnow())


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    numeber_course = Column(SmallInteger)
    name = Column(String)
    date_crate = Column(DateTime, default=datetime.datetime.utcnow())


class Item(Base):
    __tablename__ = 'items'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    subject_id = Column(BigInteger)
    telegram_id = Column(BigInteger)
    file_name = Column(String)
    file = Column(LargeBinary)
    date_crate = Column(DateTime, default=datetime.datetime.utcnow())
