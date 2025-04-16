from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, UserRole
from sqlalchemy import or_

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Recoger datos del formulario
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_str = request.form.get('role', 'consulta')
        role_enum = UserRole(role_str)
        
        # Validación básica: asegurar que se completen los campos obligatorios
        if not username or not email or not password:
            flash("Por favor, completa todos los campos obligatorios.", "warning")
            return redirect(url_for('auth.register'))
        
        # Comprobar si ya existe un usuario con el mismo nombre o email
        existing_user = User.query.filter(or_(User.username == username, User.email == email)).first()
        if existing_user:
            flash("El usuario ya existe con ese nombre de usuario o correo.", "danger")
            return redirect(url_for('auth.register'))
        
        # Crear el usuario y encriptar la contraseña
        # Asegúrate de que 'User' y 'UserRole' están correctamente definidos en app/models/user.py
        new_user = User(username=username, email=email, role=role_enum, active=True)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("¡Registro exitoso! Ahora puedes iniciar sesión.", "success")
        return redirect(url_for('auth.login'))
    
    # Método GET: mostrar el formulario de registro
    return render_template('User/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.active:
                flash("Tu cuenta está deshabilitada. Contacta con el administrador.", "danger")
                return redirect(url_for('auth.login'))
            login_user(user)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('main.index'))  # Changed from 'index' to 'main.index'
        else:
            flash("Usuario o contraseña incorrectos.", "danger")
    
    return render_template('User/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return render_template('User/logout.html')  # Updated template path


@auth_bp.route('/users')
@login_required
def user_management():
    # Add debug prints
    print(f"Current user: {current_user.username}")
    print(f"Current user role: {current_user.role}")
    
    if current_user.role != UserRole.ADMIN:
        print("Access denied: User is not admin")  # Debug print
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    print(f"Number of users found: {len(users)}")  # Debug print
    for user in users:
        print(f"User: {user.username}, Role: {user.role}")
    
    return render_template('User/user_management.html', users=users, UserRole=UserRole)


@auth_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != UserRole.ADMIN:
        flash('No tienes permisos para realizar esta acción.', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('No puedes deshabilitar tu propio usuario.', 'danger')
        return redirect(url_for('auth.user_management'))

    user.active = False  # ⚠️ No se elimina, solo se desactiva
    db.session.commit()
    flash(f'Usuario {user.username} deshabilitado correctamente.', 'success')
    return redirect(url_for('auth.user_management'))

@auth_bp.route('/enable_user/<int:user_id>')
@login_required
def enable_user(user_id):
    if current_user.role != UserRole.ADMIN:
        flash('No tienes permisos para realizar esta acción.', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    user.active = True
    db.session.commit()
    flash(f'Usuario {user.username} habilitado correctamente.', 'success')
    return redirect(url_for('auth.user_management'))

@auth_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != UserRole.ADMIN:
        flash('No tienes permisos para realizar esta acción.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = UserRole(request.form['role'])
        user.active = 'active' in request.form
        
        if request.form.get('password'):
            user.set_password(request.form['password'])
        
        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('auth.user_management'))
    
    return render_template('User/edit_user.html', user=user, roles=UserRole)
