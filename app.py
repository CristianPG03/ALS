import flask
import sirope
import flask_login
import json
from model.postDto import PostDto
from model.userDto import UserDto
from model.comentarioDto import ComentarioDto
from datetime import datetime

def create_app():
    app = flask.Flask(__name__)
    sir = sirope.Sirope()
    lm = flask_login.login_manager.LoginManager()
    app.config.from_file("config.json", json.load)
    lm.init_app(app)

    return app, sir, lm

app, sir, lm = create_app()

@lm.user_loader
def user_loader(uid:str) -> "UserDto|None":
    return UserDto.find(sir,uid)

#Si ya hay un usuario con la sesión iniciada, se muestran los posts, si no 
#se redirige a la pantalla de login
@app.route("/")
def get_index():
    usr = UserDto.current_user()
    if not usr:
        return flask.render_template('login.html')
    #listaPosts = sir.load_last(PostDto, sir.num_objs(PostDto))
    listaPosts = list(sir.load_all(PostDto))

    datos = {
        'usr':usr,
        'posts':listaPosts,
        'sirope':sir
    }

    return flask.render_template(['index.html', 'base.html'], **datos)

#Función que nos lleva a la ventana de creación de un nuevo post
@app.route('/intro_post')
def intro_post():
    fechaActual = datetime.now()
    fechaFormateada = fechaActual.strftime("%d/%m/%Y %H:%M")

    datos = {
        'usr': UserDto.current_user().email,
        'fechaActual': fechaFormateada
    }

    return flask.render_template('intro_post.html', **datos)

#Función encargada de hacer el login. Si no hay usuario lo crea y si ya existe,
#y las credenciales son correctas, lo envía a la pestaña principal
@app.route('/login', methods = ['POST'])
def login():
    nombre = flask.request.form.get("edNombre")
    email = flask.request.form.get('edEmail')
    password = flask.request.form.get('edPassword')

    usr = UserDto.current_user()

    if not usr:
        if not nombre:
            flask.flash("Introduce un nombre")
            return flask.redirect("/")

        if not email:
            flask.flash("Introduce un email válido")
            return flask.redirect("/")

        if not password:
            flask.flash("Introduce una contraseña")
            return flask.redirect("/")
        
        usr = UserDto.find(sir, email)

        if not usr:
            usr = UserDto(nombre, email, password)
        else:
            if not usr.chk_password(password):
                flask.flash("Contraseña incorrecta")
                return flask.redirect("/")

        flask_login.login_user(usr)
        sir.save(usr)
        
        return flask.redirect("/")
    
#Función para guardar un comentario dentro de un post
@app.route("/save_comment", methods=["POST"])
def save_comment():
    comentario = flask.request.form.get("edComentario")
    oid = flask.request.form.get("edOid")
    usr = UserDto.current_user()

    if not oid:
        flask.flash("OID no encontrado")
        return flask.redirect("/")

    if not usr:
       flask.flash("Necesario haber iniciado sesión")
       return flask.redirect(f"./show_post/?oid={oid}")

    if not comentario:
        flask.flash("El comentario no puede ser vacío")
        return flask.redirect(f"./show_post/?oid={oid}")
    
    post = sir.load(sir.oid_from_safe(oid))

    if not post:
        flask.flash("No se ha encontrado el post")
        return flask.redirect("/")
    
    if not post.comentarios:
        com = ComentarioDto()
    else:
        com = sir.load(post.comentarios)

    com.add_comentario(usr.nombre + ': ' + comentario)

    oidComment = sir.save(com)

    if not post.comentarios:
        post.comentarios = oidComment
        sir.save(post)

    return flask.redirect(f"./show_post/?oid={oid}")

#Función para guardar una respuesta en un comentario de un post
@app.route("/save_answer", methods=["POST"])
def save_answer():
    respuesta = flask.request.form.get('edRespuesta')
    oid = flask.request.form.get('edOid')
    comentario = flask.request.form.get('edComentario')
    usr = UserDto.current_user()

    if not oid:
        flask.flash('OID no encontrado')
        return flask.redirect("/")
    
    if not usr:
        flask.flash('Obligatorio haber iniciado sesión')
        return flask.redirect(f"./show_post/?oid={oid}")
    
    if not comentario:
        flask.flash('No hay comentario al que responder')
        return flask.redirect(f"./show_post/?oid={oid}")
    
    if not respuesta:
        flask.flash('La respuesta no puede estar vacía')
        return flask.redirect(f"./show_post/?oid={oid}")
    
    post = sir.load(sir.oid_from_safe(oid))

    if not post:
        flask.flash('No se ha encontrado el post')
        return flask.redirect('/')
    
    com = sir.load(post.comentarios)
    com.add_respuesta(comentario, usr.nombre + ": " + respuesta)
    oidComment = sir.save(com)
    if not post.comentarios:
        post.comentarios = oidComment
        sir.save(post)
    
    return flask.redirect(f"./show_post/?oid={oid}")

#Función para guardar y subir el post, comprobando que los datos están bien 
@app.route('/save_post', methods=['POST'])
def save_post():
    textoPost = flask.request.form.get("edTexto")
    fechaPost = flask.request.form.get("edFechaActual")
    usr = UserDto.current_user()

    if not usr:
        flask.flash("Necesario haber iniciado sesión")
        return flask.redirect("/")

    if not textoPost:
        flask.flash("El contenido del post no puede ser vacío")
        return flask.redirect("/intro_post")

    if not fechaPost:
        flask.flash("Ha ocurrido un error con la fecha")
        return flask.redirect("/intro_post")
    
    sir.save(PostDto(usr.email, textoPost, usr.nombre, fechaPost))
    return flask.redirect("/")

#Función que nos lleva a una ventana donde se muestra el post seleccionado,
#en el que se verá información adicional como los comentarios y respuestas
@app.route('/show_post/')
def show_post():
    oid = flask.request.args.get('oid')
    usr = UserDto.current_user()

    if not usr:
        flask.flash("Necesario haber iniciado sesión")
        return flask.redirect("/")
    
    if not oid:
        flask.flash('OID no encontrado')
        return flask.redirect("/")
    
    try:
        post = sir.load(sir.oid_from_safe(oid))
    except:
        flask.flash('No se ha encontrado el post')
        return flask.redirect("/")
    
    comentarios = {}
    if post.comentarios:
        comentarios = sir.load(post.comentarios).comentarios

    datos = {
        'post': post,
        'comentarios': comentarios,
        'usr': usr.email,
        'oid': oid
    }

    return flask.render_template("post.html", **datos)

#Función para borrar el post. SOLO se pueden borrar los post creados por el
#usuario
@app.route('/del_post/')
def del_post():
    oid = flask.request.args.get('oid')
    usr = UserDto.current_user()

    if not usr:
        flask.flash("Necesario haber iniciado sesión")
        return flask.redirect("/")

    if not oid:
        flask.flash("OID no encontrado")
        return flask.redirect("/")

    sir.delete(sir.oid_from_safe(oid))

    return flask.redirect("/")

#Función para cerrar la sesión
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect("/")

@lm.unauthorized_handler
def unauthorized():
    return "No autorizado", 401

if __name__ == '__main__':
    app.run()