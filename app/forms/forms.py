from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, BooleanField, RadioField, DateField, IntegerField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Optional, Email
from app.models.solicitud_subvencion import EstadoSolicitud

class FormularioSolicitud(FlaskForm):
    # Datos generales
    expediente_opensea = StringField("Expediente OpenSea", validators=[DataRequired()])
    expediente_subvencion = StringField("Expediente Subvención", validators=[DataRequired()])
    entidad_id = IntegerField("Entidad ID", validators=[DataRequired()])
    concepto = StringField("Concepto", validators=[DataRequired()])
    tipo_fondo = SelectField("Tipo de Fondo", choices=[
        ("Europeo", "Europeo"),
        ("Nacional", "Nacional"),
        ("Autonómico", "Autonómico"),
        ("Provincial", "Provincial"),
        ("Otros", "Otros")
    ], validators=[DataRequired()])

    estado = RadioField("Estado", choices=[
        ("en_tramite", "En trámite"),
        ("no_solicitada", "No solicitada"),
        ("solicitada", "Solicitada"),
        ("alegaciones", "Alegaciones"),
        ("concedida_provisional", "Concedida provisional"),
        ("concedida", "Concedida"),
        ("denegada", "Denegada")
    ], validators=[DataRequired()])

    # Información económica
    presupuesto = FloatField("Presupuesto", validators=[Optional()])
    subvencion_solicitada = FloatField("Subvención Solicitada", validators=[Optional()])
    subvencion_concedida = FloatField("Subvención Concedida", validators=[Optional()])

    # Fechas clave
    fecha_limite_presentacion = DateField("Fecha límite de presentación", format='%Y-%m-%d', validators=[DataRequired()])
    fecha_presentacion_solicitud = DateField("Fecha de presentación", format='%Y-%m-%d', validators=[Optional()])
    fecha_resolucion_provisional = DateField("Fecha resolución provisional", format='%Y-%m-%d', validators=[Optional()])
    fecha_resolucion_definitiva = DateField("Fecha resolución definitiva", format='%Y-%m-%d', validators=[Optional()])

    # Documentación
    doc_inicio_expediente = BooleanField("Doc. Inicio Expediente")
    doc_informe_tecnico = BooleanField("Doc. Informe Técnico")
    doc_propuesta_jgl = BooleanField("Doc. Propuesta JGL")
    doc_ficha_captacion = BooleanField("Doc. Ficha Captación")

    # Gestión
    motivo_no_solicitada = TextAreaField("Motivo No Solicitada", validators=[Optional()])
    motivo_denegada = TextAreaField("Motivo Denegada", validators=[Optional()])
    gestor_responsable = StringField("Gestor Responsable", validators=[Optional()])
    email_gestor = EmailField("Email Gestor", validators=[Optional(), Email()])

    def validate(self):
        is_valid = super().validate()
        if not is_valid:
            return False

        errores = False
        estado = self.estado.data

        if estado == 'no_solicitada' and not self.motivo_no_solicitada.data.strip():
            self.motivo_no_solicitada.errors.append("Este campo es obligatorio si la solicitud no se ha presentado.")
            errores = True

        if estado == 'denegada' and not self.motivo_denegada.data.strip():
            self.motivo_denegada.errors.append("Debes indicar por qué fue denegada.")
            errores = True

        if estado == 'concedida' and not self.fecha_resolucion_definitiva.data:
            self.fecha_resolucion_definitiva.errors.append("Requiere fecha de resolución definitiva.")
            errores = True

        if estado == 'concedida_provisional' and not self.fecha_resolucion_provisional.data:
            self.fecha_resolucion_provisional.errors.append("Requiere fecha de resolución provisional.")
            errores = True

        return not errores
