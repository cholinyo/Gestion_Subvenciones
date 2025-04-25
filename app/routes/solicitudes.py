from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import func
from datetime import date, datetime

from app import db
from app.models.solicitud_subvencion import SolicitudSubvencion, EstadoSolicitud
from app.models.observacion_solicitud import ObservacionSolicitud
from app.utils.historial import registrar_historial
from app.utils.validate_solicitud_estado import parse_float, validate_solicitud_estado
from app.forms.forms import FormularioSolicitud  # Asegúrate de importar correctamente

solicitudes_bp = Blueprint("solicitudes", __name__)

def parse_fecha(nombre_campo):
    valor = request.form.get(nombre_campo)
    return datetime.strptime(valor, "%Y-%m-%d").date() if valor else None


# -------------------- RUTA: LISTADO --------------------
@solicitudes_bp.route("/solicitudes")
@login_required
def lista_solicitudes():
    estado_filtrado = request.args.get("estado")
    concepto_busqueda = request.args.get("concepto", "").strip().lower()
    expediente_busqueda = request.args.get("expediente", "").strip().lower()
    per_page = request.args.get("per_page", type=int, default=10)
    page = request.args.get("page", type=int, default=1)

    query = SolicitudSubvencion.query

    if estado_filtrado:
        valores_validos = [e.value for e in EstadoSolicitud]
        if estado_filtrado in valores_validos:
            estado_enum = EstadoSolicitud(estado_filtrado)
            query = query.filter(SolicitudSubvencion.estado == estado_enum)
        else:
            flash(f"Estado no válido: {estado_filtrado}", "danger")
            return redirect(url_for("solicitudes.lista_solicitudes"))

    if concepto_busqueda:
        query = query.filter(SolicitudSubvencion.concepto.ilike(f"%{concepto_busqueda}%"))

    if expediente_busqueda:
        query = query.filter(SolicitudSubvencion.expediente_subvencion.ilike(f"%{expediente_busqueda}%"))

    paginated = query.order_by(SolicitudSubvencion.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    estadisticas = (
        db.session.query(SolicitudSubvencion.estado, func.count(SolicitudSubvencion.id))
        .group_by(SolicitudSubvencion.estado)
        .all()
    )

    proximas_solicitudes = (
    SolicitudSubvencion.query
    .filter(
        SolicitudSubvencion.estado == EstadoSolicitud.EN_TRAMITE,
        SolicitudSubvencion.fecha_limite_presentacion >= date.today(),
        SolicitudSubvencion.fecha_limite_presentacion != None
    )
    .order_by(SolicitudSubvencion.fecha_limite_presentacion.asc())
    .limit(5)
    .all()

    )

    return render_template(
    "solicitudes/lista.html",
    solicitudes=paginated.items,
    pagination=paginated,
    estado_filtrado=estado_filtrado,
    concepto_busqueda=concepto_busqueda,
    expediente_busqueda=expediente_busqueda,
    per_page=per_page,
    estadisticas=estadisticas,
    proximas_solicitudes=proximas_solicitudes,
    today=date.today()
    )

# -------------------- RUTA: NUEVA --------------------
@solicitudes_bp.route("/solicitud/nueva", methods=["GET", "POST"])
@login_required
def nueva_solicitud():
    if request.method == "POST":
        estado = request.form.get("estado")
        motivo_no_solicitada = request.form.get("motivo_no_solicitada")
        fecha_limite = parse_fecha("fecha_limite_presentacion")

        if not fecha_limite:
            flash("Debes indicar la fecha límite de presentación.", "danger")
            return render_template("solicitudes/nueva.html")

        if estado == "no_solicitada" and not motivo_no_solicitada:
            flash("Debes indicar el motivo por el que no se ha solicitado.", "danger")
            return render_template("solicitudes/nueva.html")

        solicitud = SolicitudSubvencion(
            expediente_opensea=request.form.get("expediente_opensea"),
            expediente_subvencion=request.form.get("expediente_subvencion"),
            entidad_id=request.form.get("entidad_id"),
            concepto=request.form.get("concepto"),
            tipo_fondo=request.form.get("tipo_fondo"),
            gestor_responsable=current_user.username,
            email_gestor=current_user.email,
            fecha_limite_presentacion=fecha_limite,
            motivo_no_solicitada=motivo_no_solicitada,
            estado=EstadoSolicitud(estado) if estado else EstadoSolicitud.EN_TRAMITE
        )

        db.session.add(solicitud)
        db.session.commit()
        flash("Solicitud creada correctamente.", "success")
        return redirect(url_for("solicitudes.editar_solicitud", solicitud_id=solicitud.id))

    return render_template("solicitudes/nueva.html")


# -------------------- RUTA: EDITAR --------------------
@solicitudes_bp.route("/solicitud/<int:solicitud_id>/editar", methods=["GET", "POST"])
@login_required
def editar_solicitud(solicitud_id):
    solicitud = SolicitudSubvencion.query.get_or_404(solicitud_id)

    form = FormularioSolicitud(obj=solicitud)
    estado_anterior = solicitud.estado

    if form.validate_on_submit():
        form.populate_obj(solicitud)

        # Validación adicional de estado si es necesario
        nuevo_estado = EstadoSolicitud(form.estado.data)
        solicitud.estado = nuevo_estado

        try:
            validate_solicitud_estado(solicitud, estado_anterior=estado_anterior)
        except ValueError as e:
            flash(str(e), "danger")
            return render_template("solicitudes/editar.html", solicitud=solicitud, form=form)

        # Historial si cambia el estado
        if nuevo_estado != estado_anterior:
            descripcion = f"Estado cambiado de {estado_anterior.value} a {nuevo_estado.value}"
            registrar_historial(solicitud, current_user, descripcion)

        # Registrar observación si viene texto
        texto_observacion = request.form.get("observaciones")
        if texto_observacion:
            nueva_obs = ObservacionSolicitud(
                solicitud_id=solicitud.id,
                usuario_id=current_user.id,
                texto=texto_observacion,
                fecha=datetime.utcnow()
            )
            db.session.add(nueva_obs)

        db.session.commit()
        flash("Solicitud actualizada correctamente.", "success")
        return redirect(url_for("solicitudes.ver_solicitud", solicitud_id=solicitud.id))

    return render_template("solicitudes/editar.html", solicitud=solicitud, form=form)

# -------------------- RUTA: VER --------------------
@solicitudes_bp.route("/solicitud/<int:solicitud_id>")
@login_required
def ver_solicitud(solicitud_id):
    solicitud = SolicitudSubvencion.query.get_or_404(solicitud_id)
    historial = solicitud.historial

    return render_template(
        "solicitudes/ver.html",
        solicitud=solicitud,
        historial=historial,
        ObservacionSolicitud=ObservacionSolicitud
    )


# -------------------- RUTA: AÑADIR OBSERVACIÓN --------------------
@solicitudes_bp.route("/solicitud/<int:solicitud_id>/observacion", methods=["POST"])
@login_required
def añadir_observacion(solicitud_id):
    solicitud = SolicitudSubvencion.query.get_or_404(solicitud_id)
    texto = request.form.get("observacion", "").strip()

    if not texto:
        flash("La observación no puede estar vacía.", "warning")
        return redirect(url_for("solicitudes.ver_solicitud", solicitud_id=solicitud.id))

    observacion = ObservacionSolicitud(
        solicitud_id=solicitud.id,
        usuario_id=current_user.id,
        texto=texto
    )

    db.session.add(observacion)
    db.session.commit()

    flash("Observación añadida correctamente.", "success")
    return redirect(url_for("solicitudes.ver_solicitud", solicitud_id=solicitud.id))
