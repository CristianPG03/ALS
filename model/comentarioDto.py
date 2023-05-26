from datetime import datetime

#El comentario se guardara de la siguiente manera:
# {comentario: [respuestas]}
class ComentarioDto:
    def __init__(self):
        self._comentarios = {}

    @property
    def comentarios(self):
        return self._comentarios
    
    @comentarios.setter
    def comentarios(self, com):
        self._comentarios = com
    
    #Añadir comentario
    def add_comentario(self, com: str):
        hora = datetime.now()
        d = hora.day
        m = hora.month
        a = hora.year
        h = hora.hour
        min = hora.minute
        self.comentarios.update({f" | {d:02d}/{m:02d}/{a:02d} {h:02d}:{min:02d} |  {com}":list()})

    #Añadir respuesta al comentario
    def add_respuesta(self, com: str, res: str):
        hora = datetime.now()
        d = hora.day
        m = hora.month
        a = hora.year
        h = hora.hour
        min = hora.minute
        self.comentarios[com].append(f" | {d:02d}/{m:02d}/{a:02d} {h:02d}:{min:02d} |  {res}")