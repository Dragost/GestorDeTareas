# -*-coding: utf-8 -*-

#IMPORTS:

from flask import Flask, render_template, request, flash, session, url_for, redirect, g, abort
from forms import ContactForm, AltaForm, LoginForm, FormTarea, FormEditarTarea
from flask.ext.mail import Message, Mail
from functools import wraps
from models import Base, User, Tareas
from flask.ext.sqlalchemy import SQLAlchemy
 
#CONFIGURACIÓN
 
app = Flask(__name__)
app.secret_key = '\x84\xed\xca\xe36\x8d\x17\xd4\xb3X\xfd1\xdfJx\xc6\xe9\xcf\x00\xdf\x9e \xa9l'

#mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'dragost11@gmail.com'
app.config["MAIL_PASSWORD"] = '' # Cambiar

#SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tareas.db'

#captcha
app.config["RECAPTCHA_PUBLIC_KEY"] = '6LeJmeoSAAAAAGAv9mSzRk-mKEE3I8i1LoqjClcA'
app.config["RECAPTCHA_PRIVATE_KEY"] = '6LeJmeoSAAAAAG38d7TBJqN5TPumnh80pVYwORL3'

#mail 
mail = Mail()
mail.init_app(app)

# SQL Alchemy
db = SQLAlchemy(app)
db.Model = Base

      

#RUTAS PRINCIPALES

#Home
@app.route('/')
def home():
    '''
    método para ir a home
    '''
    return render_template('home.html')

#About
@app.route('/nosotros')
def about():
    '''
    método para ir a la página about we.
    '''
    return render_template('about.html')

#Contacto 
@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    '''
    método para enviar formulario de contacto al mail del admin.
    '''
    form = ContactForm()
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('contacto.html', form=form)
        else:
            msg = Message(form.subject.data, sender='dragost11@gmail.com', recipients=['dragost11@gmail.com'])
            msg.body = """
              Mensaje de: %s <%s>
              %s
              """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            
            return render_template('contacto.html', nombre=form.name.date, success=True)
    else:
        return render_template('contacto.html', form=form)

#GESTIÓN DE USUARIO

#Alta
@app.route('/alta', methods=['GET', 'POST'])
def alta():
    '''
    método para registrar usuario en BD.
    '''
    form = AltaForm(db=db)
    if 'email' in session:
        return redirect(url_for('tareas'))
   
    if request.method == 'POST':
        if form.validate(db) == False:
            return render_template('alta.html', form=form)
        else: 
            newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit() 
            session['email'] = newuser.email
            user = db.session.query(User).filter_by(email = session['email']).first()
            session['uid']=user.uid
            return redirect(url_for('tareas'))
   
    elif request.method == 'GET':
        return render_template('alta.html', form=form)
    
#Loguearse
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    método login. Si usuario existe se crea la sesión
    '''
    form = LoginForm(db=db)
    if 'email' in session:
        return redirect(url_for('tareas'))
   
    if request.method == 'POST':
        if form.validate(db) == False:
            return render_template('login.html', form=form)
        else:
            session['email'] = form.email.data
            user = db.session.query(User).filter_by(email = session['email']).first()
            session['uid']=user.uid
            #redirección a próximo o a home 
            return redirect(request.args.get("next") or url_for("tareas"))
    else:
        return render_template('login.html', form=form) 

#Decorador de login requerido
def login_required(f):
    '''
    método para crear decorador de login requerido (se coloca antes de usuarlo porque si no, no funciona).
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#Desloguearse
@app.route('/logout')
@login_required
def logout():
    '''
    método que elimina la sesión
    '''
    session.pop('email', None)
    session.pop ('uid', None)
    return redirect(url_for('home'))

#6Baja de usuarios
@app.route('/baja')
@login_required
def baja():
    '''
    método que únicamente redirige a otro, para que se confirme la baja de usuario.
    '''
    user = db.session.query(User).filter_by(email = session['email']).first()
    return render_template('baja.html',user=user)

#Confirmación baja de usuario 
@login_required
@app.route('/bajadefinitiva')
def baja_definitiva():
    '''
    método elimina de la BD al baja de usuario.
    Dado que la sesión sigue creada, se elimina una vez producida la baja, para que usuario no registrado no siga logueado
    '''
    user = db.session.query(User).filter_by(email = session['email']).first()
    #Eliminamos usuario
    db.session.delete(user)
    db.session.commit()
    #Eliminamos la sesión 
    session.pop('email', None)
    session.pop ('uid', None)
    return redirect(url_for('home'))
   


#TAREAS

#Listado tareas
@login_required
@app.route('/tareas/')
def tareas():
    '''
    Método para listar las tareas.
    Se hacen dos búsquedas en la base de datos, una de tareas realizadas y otra de pendientes
    Se pasan las dos búsquedas a la plantilla para que se presenten por separado (por requisitos)
    '''
    user = db.session.query(User).filter_by(email = session['email']).first()
    realizadas = (db.session.query(Tareas).filter_by(user_id=user.uid, terminada = True).order_by(Tareas.fecha_realizacion.desc()).all())
    pendientes = (db.session.query(Tareas).filter_by(user_id=user.uid, terminada = False).order_by(Tareas.creada.desc()).all())
    return render_template('tareas/tareas.html',realizadas=realizadas, pendientes=pendientes,user=user)

#crear tareas
@app.route('/tareas/nueva/', methods=['GET', 'POST'])
@login_required
def crear_tareas():
    '''
    Método para crear una nueva tarea
    '''
    form = FormTarea(request.form)
    
    if request.method == 'POST' and form.validate():
        tarea = Tareas(user_id=session['uid'])
        form.populate_obj(tarea)
        db.session.add(tarea)
        db.session.commit()
        return redirect(url_for('tareas'))
    return render_template('tareas/nueva.html', form=form)

#Detalle de tareas + modificar tareas
@app.route('/tareas/<int:tareas_id>/', methods=['GET', 'POST'])
@login_required
def detalle_tarea(tareas_id):
    '''
    El método presenta el detalle de la tarea.
    Por cuestiones de usabilidad, se ha decidido que desde la misma vista de usuario se puede editar la tarea
    '''
    tarea = db.session.query(Tareas).get(tareas_id)
    form = FormEditarTarea(request.form)
    if request.method == 'POST': 
        if form.validate() == False:
            tarea.fecha_realizacion = tarea.fecha_realizacion
            return render_template('tareas/detalle.html', form=form, tarea=tarea )
        else:
            if form.fecha_realizacion.data == None:
                tarea.fecha_realizacion = tarea.fecha_realizacion
            else:
                tarea.fecha_realizacion = form.fecha_realizacion.data
        if form.prioridad.data != tarea.prioridad:
            tarea.prioridad = form.prioridad.data
        if tarea.terminada == True: 
            tarea.terminada = tarea.terminada
        else:    
            if form.terminada.data != tarea.terminada:
                tarea.terminada = form.terminada.data
        if form.descripcion.data != tarea.descripcion and form.descripcion.data != '':
            tarea.descripcion = form.descripcion.data
        db.session.commit()
        return redirect(url_for('tareas'))
    else:
        return render_template('tareas/detalle.html', form=form, tarea=tarea)

#Eliminar tareas
@app.route('/tareas/<int:tarea_id>/eliminar')
@login_required
def eliminar_tarea(tarea_id):
    '''
    Método para eliminar la tarea (no requiere confirmación)
    '''
    tarea = db.session.query(Tareas).filter_by(id = tarea_id).first()
    db.session.delete(tarea)
    db.session.commit()
    return redirect(url_for('tareas'))

if __name__ == '__main__':
    app.run(debug=True)
