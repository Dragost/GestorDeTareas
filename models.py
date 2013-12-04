#!/usr/bin/env python
# -*-coding: utf-8 -*-

#IMPORTS
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from datetime import *

Base=declarative_base()

#Clase para usuarios
class User(Base):
    __tablename__ = 'users'
    uid = Column(Integer, primary_key = True)
    firstname =Column(String(100))
    lastname = Column(String(100))
    email = Column(String(120), unique=True)
    pwdhash =Column(String(200))
   
    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(password)
     
    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)#El password ya va cifrado.
   
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)
    
    def __unicode__(self):
        return "%s %s (%s)" %(self.firstname, self.lastname, self.email)

#Clase Tareas
class Tareas(Base):
    __tablename__ = 'tareas'
 
    id = Column(Integer, primary_key=True)
    creada = Column(DateTime, default=date.today)
    tarea = Column(String(255))
    fecha_realizacion= Column(String)
    prioridad = Column (String (100), nullable=False)
    terminada = Column(Boolean, default=False)
    descripcion = Column(Text)
    user_id = Column(Integer, ForeignKey('users.uid'), nullable=False)
    usuario = relationship(User, lazy='joined', join_depth=1, viewonly=True)
    
    
 
    def __unicode__(self):
        return "{tarea} [{creada}}".format(tarea=self.tarea,
            fecha_realizacion=self.fecha_realizacion)

'''
Creamos la base de datos SQ Lite
'''
if __name__ == '__main__':
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///tareas.db', echo=True)

    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    
    
   
    