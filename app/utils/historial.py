# app/utils/historial.py

def registrar_historial(solicitud, usuario, descripcion):
    from app.models.historial_solicitud import HistorialSolicitud

    entrada = HistorialSolicitud(
        solicitud_id=solicitud.id,
        usuario_id=usuario.id,
        descripcion=descripcion
    )
    from app import db
    db.session.add(entrada)
    db.session.commit()
