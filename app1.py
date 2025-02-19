from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash


import mysql.connector

app = Flask(__name__)
app.secret_key = 'clave_secreta'

def conectar_bd():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='asistencia1'
    )




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        conexion=conectar_bd()
        cursor = conexion.cursor(dictionary=True)

        #hash_contrasena = generate_password_hash(contrasena1)

       # Consultar el usuario en la base de datos
        cursor.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        conexion.close()

        # Verificar si el usuario existe y si la contraseña es correcta
        if usuario and check_password_hash(usuario['contrasena'], contrasena):
            session['usuario_id'] = usuario['id_usuario']
            session['rol'] = usuario['id_rol']
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/dashboard')

def dashboard():
    if 'usuario_id' not in session:
        flash('Debe iniciar sesión primero', 'danger')
        return redirect(url_for('login'))
    
    if session['rol'] == 1:  # Administrador
        return render_template('dashboard_admin.html')
    elif session['rol'] == 2:  # Docente
        return render_template('dashboard_docente.html')
    elif session['rol'] == 3:  # Padre
        return render_template('dashboard_padre.html')
    else:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('logout'))

# Decorador para restringir acceso por rol
def requiere_rol(roles_permitidos):
    def decorador(func):
        def envoltura(*args, **kwargs):
            if 'usuario_id' not in session or session['rol'] not in roles_permitidos:
                flash('Acceso no autorizado', 'danger')
                return redirect(url_for('dashboard'))
            return func(*args, **kwargs)
        return envoltura
    return decorador 

@app.route('/generar_reporte', methods=['GET'])
@requiere_rol([3])  # Solo padres pueden generar reportes

def generar_reporte_padre():
    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)
    usuario_id = session['usuario_id']
    
    print("Usuario ID en sesión:", session.get('usuario_id'))

    # Obtener hijos del padre
    cursor.execute("SELECT * FROM estudiante WHERE id_usuario = %s", (usuario_id,))
    hijos = cursor.fetchall()
    
    # Obtener materias
    cursor.execute("SELECT * FROM materia")
    materias = cursor.fetchall()
    
    reporte = [] 
    if request.args:
        hijo_id = request.args.get('hijo')
        materia_id = request.args.get('materia')
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        consulta = """
        SELECT registro.fecha, materia.nombre_materia AS materia, registro.estado 
        FROM registro 
        JOIN materia ON registro.materia = materia.id_materia
        WHERE registro.estudiante = %s AND registro.fecha BETWEEN %s AND %s
        """
        params = [hijo_id, fecha_inicio, fecha_fin]
        
        if materia_id:
            consulta += " AND registro.materia = %s"
            params.append(materia_id)
        
        cursor.execute(consulta, tuple(params))
        reporte = cursor.fetchall()
    
    conexion.close()
    return render_template('dashboard_padre.html', hijos=hijos, materias=materias, reporte=reporte)


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('login'))


#if __name__ == '__main__':
 #   app.run(debug=True)
