from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///antg.db')
engine.connect()
Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column('id', Integer(), primary_key=True)
    name = Column('name', String(200))
    admin = Column('admin', Boolean(), default=False)


class Districts(Base):
    __tablename__ = 'districts'
    id = Column('id', Integer(), primary_key=True)
    name = Column('name', String(200))
    called = Column('called', Integer(), default=0)


class Themes(Base):
    __tablename__ = 'themes'
    id = Column('id', Integer(), primary_key=True)
    name = Column('name', String(200))


class AdmDist(Base):
    __tablename__ = 'adm_dist'
    id = Column('id', Integer(), primary_key=True)
    name = Column('name', String(200))
    called = Column('called', Integer(), default=0)


class Places(Base):
    __tablename__ = 'places'
    id = Column('id', Integer(), primary_key=True)
    name = Column('name', String(200))
    description = Column('description', String(800))
    price_min = Column('price_min', Integer())
    price_max = Column('price_max', Integer())
    date_start = Column('date_start', DateTime())
    date_end = Column('date_end', DateTime())
    theme = Column('theme', ForeignKey("themes.id"))
    image = Column('image', String(200))
    address = Column('address', String(200))
    lat = Column('lat', Float())
    lon = Column('lon', Float())
    priority = Column('priority', Integer(), default=0)


Session = sessionmaker(bind=engine)
