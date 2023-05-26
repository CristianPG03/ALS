class PostDto:
    def __init__(self, userPost, textPost, userName, postFecha):
        self._userPost = userPost #Email del usuario que sube el post
        self._textPost = textPost #Contenido del post
        self._userName = userName #Nombre del usuario que hace el post
        self._postFecha = postFecha #Fecha de la publicación del post
        self._comentarios = None   #Comentarios del post

    @property
    def userPost(self):
        return self._userPost
    
    @property
    def textPost(self):
        return self._textPost
    
    @property
    def userName(self):
        return self._userName
    
    @property
    def postFecha(self):
        return self._postFecha
    
    @property
    def comentarios(self):
        return self._comentarios
    
    @comentarios.setter
    def comentarios(self, com):
        self._comentarios = com

    def __str__(self):
        return f"{self.userName}({self.userPost}):\n {self.textPost}"