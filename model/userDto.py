import sirope
import flask_login
import werkzeug.security as safe

class UserDto(flask_login.UserMixin):
    def __init__(self, nombre, email, password):
        self._nombre = nombre   #Nombre del usuario
        self._email = email     #Email del usuario
        self._password = safe.generate_password_hash(password)  #Contraseña del usuario
    
    @property
    def nombre(self):
        return self._nombre
    
    @property
    def email(self):
        return self._email
    
    def get_id(self):
        return self.email
    
    def chk_password(self, pswd):
        return safe.check_password_hash(self._password, pswd)
    
    @staticmethod
    def current_user() -> "UserDto|None":   #Metodo que devuelve el usuario actual
        usr = flask_login.current_user
        
        if usr.is_anonymous:
            flask_login.logout_user()
            usr = None
    
        return usr
    
    @staticmethod
    def find(s: sirope.Sirope, email: str) -> "UserDto":    #Metodo para buscar un usuario
        return s.find_first(UserDto, lambda u: u.email == email)