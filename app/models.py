from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

from app import db

class Carga_Documentos(db.Model):

    __tablename__ = 'bitacora_carga_documentos'

    id = db.Column(db.Integer, primary_key = True)
    #empresa = db.Column(db.String(256), nullable = False)
    clave_empresa = db.Column(db.String(256), nullable = False)
    rfc = db.Column(db.String(256), nullable = False)
    tipo_documento = db.Column(db.String(256), nullable = False)
    nombre_documento = db.Column(db.String(256), nullable = False)
    texto_documento = db.Column(db.Text, nullable = False)
    informacion_documento = db.Column(JSON)
    url_google_cloud = db.Column(db.String(256), nullable = False)
    fecha_carga = db.Column(db.DateTime, default = datetime.utcnow)
    #token = db.Column(db.String(256), nullable = False)

    def __repr__(self):
        return f'<Upload {self.nombre_documento}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Bitacora_Consultas(db.Model):

    __tablename__ = 'bitacora_consultas'

    id = db.Column(db.Integer, primary_key = True)
    #empresa = db.Column(db.String(256), nullable = False)
    clave_empresa = db.Column(db.String(256), nullable = False)
    rfc = db.Column(db.String(256), nullable = False)
    tipo_documento = db.Column(db.String(256), nullable = False)
    fecha_consulta = db.Column(db.DateTime, default = datetime.utcnow)
    #oken = db.Column(db.String(256), nullable = False)

    def __repr__(self):
        return f'<Buscar: {self.RFC} - {self.tipo_documento}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()