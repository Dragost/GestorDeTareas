# -*-coding: utf-8 -*-

#IMPORTS:

from wtforms import TextField, TextAreaField, SubmitField, validators, SelectField, PasswordField, BooleanField, DateField
from models import User, Base, Tareas
from flask_wtf import Form, RecaptchaField

#Formulario contacto
class ContactForm(Form):
    name = TextField("Nombre",  [validators.Required("Introduzca su nombre")])
    email = TextField("Email",  [validators.Required("Introduzca su email"), validators.Email("Introduzca un mail correcto")])
    subject = TextField("Asunto",  [validators.Required("Indique un asunto")])
    message = TextAreaField("Mensaje",  [validators.Required("Escríbanos su mensaje")])
    submit = SubmitField("Enviar")

#Formulario Alta  
class AltaForm(Form):
    firstname = TextField("Nombre",  [validators.Required("Introduzca su nombre")])
    lastname = TextField("Apellido",  [validators.Required("Introduzca su apellido.")])
    email = TextField("Email",  [validators.Required("Ingrese email."), validators.Email("Ingrese un mail correcto")])
    password = PasswordField('Contraseña', [validators.Required("Introduzca contraseña.")])
    submit = SubmitField("Crear cuenta")
    recaptcha = RecaptchaField()
 
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
 
    def validate(self,db):
        if not Form.validate(self):
            return False
        user = db.session.query(User).filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append("El email ya existe.")
            return False
        else:
            return True

#formulario login
class LoginForm(Form):
    email = TextField("Email",  [validators.Required("Por favor ingrese su email"), validators.Email("Por favor ingrese su email.")])
    password = PasswordField('Password', [validators.Required("Introduca la contraseña.")])
    submit = SubmitField("Login")
   
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
 
    def validate(self,db):
        if not Form.validate(self):
            return False
        user = db.session.query(User).filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append("Usuario o contraseña no encontrados")
            return False
        

#Formulario Tareas.
class FormTarea(Form):
    
    tarea = TextField('Tarea', [validators.Length(max=255)])
    fecha_realizacion = DateField('Fecha (formato dd/mm/aaaa)',[validators.Required("Introduzca una fecha")], format='%d/%m/%Y')
    prioridad = SelectField('Prioridad', choices=[('alta', 'alta'), ('normal', 'normal'),('baja', 'baja')])
    terminada = BooleanField('Marcar como realizada')
    descripcion = TextAreaField('Descripción')
    submit = SubmitField("Crear tarea")

#Formulario editar tareas
class FormEditarTarea(Form):
    
    fecha_realizacion = DateField('Modificar fecha (formato dd/mm/aaaa)', [validators.Optional(), validators.Required("formato de fecha incorrecto")], format='%d/%m/%Y')
    prioridad = SelectField('Modificar prioridad', choices=[('alta', 'alta'), ('normal', 'normal'),('baja', 'baja')])
    terminada = BooleanField('Marcar como realizada')
    descripcion = TextAreaField('modificar descripción')
    submit = SubmitField("Guardar cambios")
