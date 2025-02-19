import mysql.connector
from mysql.connector import Error
import pymysql
from datetime import datetime
import requests
from threading import Thread
from diccionario import guardar_estudiantes_en_diccionario

def conectar_bd():
    """Conecta a la base de datos MySQL y devuelve la conexión."""
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='asistencia'
        )
        return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def obtener_estudiantes():
    """Obtiene la lista de estudiantes desde la base de datos."""
    conexion = conectar_bd()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estudiante")
        estudiantes = cursor.fetchall()
        return estudiantes
    except Error as e:
        print(f"Error al obtener estudiantes: {e}")
        return []
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def agregar_estudiante(ci, apellidos, nombres, curso, foto, ppff):
    """Agrega un nuevo estudiante a la base de datos."""
    conexion = conectar_bd()
    if not conexion:
        return False

    try:
        cursor = conexion.cursor()
        query = (
            "INSERT INTO estudiante (CI, apellidos, nombres, curso, foto, ppff) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(query, (ci, apellidos, nombres, curso, foto, ppff))
        conexion.commit()
        return True
    except Error as e:
        print(f"Error al agregar estudiante: {e}")
        return False
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def get_user_credentials(username):
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="asistencia"
    )
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id_docente, CI FROM docente WHERE id_docente = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                return {"username": result[0], "password": result[1]}
    finally:
        connection.close()
    return None

# Función para obtener la lista de cursos
def obtener_cursos():
    connection = conectar_bd()
    try:
        cursor = connection.cursor()
        try:
            query = "SELECT id_curso, nombre_curso FROM curso"
            cursor.execute(query)
            resultados = cursor.fetchall()  # Devuelve una lista de diccionarios
            # Convertir tuplas a diccionarios
            cursos = [{"id_curso": fila[0], "nombre_curso": fila[1]} for fila in resultados]
        finally:
            cursor.close()  # Asegura que el cursor se cierre
        return cursos
    finally:
        connection.close()  # Asegura que la conexión se cierre

# Función para obtener la lista de materias
def obtener_materias():
    connection = conectar_bd()
    try:
        cursor = connection.cursor()
        try:
            query = "SELECT id_materia, nombre_materia FROM materia"
            cursor.execute(query)
            resultados2 = cursor.fetchall()  # Devuelve una lista de diccionarios
            # Convertir tuplas a diccionarios
            materias = [{"id_materia": fila[0], "nombre_materia": fila[1]} for fila in resultados2]
        
        finally:
            cursor.close()  # Asegura que el cursor se cierre
        return materias
    finally:
        connection.close()  # Asegura que la conexión se cierre

'''def obtener_estudiantes_info():
    connect = conectar_bd()
    cursor = connect.cursor(dictionary=True)
    
    consulta = "SELECT * FROM estudiante"
    estudiantes_info = {}

    try:
        cursor.execute(consulta)
        resultados = cursor.fetchall()
        
        for fila in resultados:
            nombre = fila["apellidos"]
            estudiantes_info[nombre] = {
                "id_estudiante":fila["id_estudiante"],
                "apellidos": fila["apellidos"],
                "nombres":fila['nombres'],
                "curso": fila["curso"],
                "foto": fila["foto"],
                "ppff": fila["ppff"]
            }
        print("Información de estudiantes cargada correctamente.")
        print(estudiantes_info)
    except Exception as e:
        print(f"Error al cargar información de estudiantes: {e}")
    finally:
        cursor.close()
        connect.close()
    
    return estudiantes_info'''

##### Obneter datos desde API ###########

# Función para obtener datos desde la API
'''def obtener_datos_desde_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al recuperar datos desde la API: {e}")
        return []
'''
asistencia_registrada = {}

def guardar_estudiantes_en_diccionario():
    """
    Obtiene la lista de estudiantes desde la base de datos
    y los guarda en un diccionario.
    """
    estudiantes = obtener_estudiantes()  # Llama a la función que obtiene los estudiantes
    #print(estudiantes)
    
    if not estudiantes:
        print("No se encontraron estudiantes o hubo un error al obtenerlos.")
        
        return {}

    # Crear un diccionario donde la clave sea el ID del estudiante
    diccionario_estudiantes = {estudiante['id_estudiante']: estudiante for estudiante in estudiantes}
    
    return diccionario_estudiantes
    
#estudiantes_diccionario = guardar_estudiantes_en_diccionario()

def guardar_asistencia(id_estudiante, curso, materia):
    connection=conectar_bd()
    cursor = connection.cursor()
    est=obtener_estudiantes()
    # Obtener fecha y hora actuales
    ahora = datetime.now()
    fecha = ahora.date()
    hora = ahora.time()
     

    '''if estudiantes_diccionario:
        #print("Estudiantes guardados en el diccionario:")
        for id_estudiante, datos in estudiantes_diccionario.items():
            print(f"ID: {id_estudiante}, Datos: {datos}")'''
    '''try:
        # Insertar registro en la tabla
        consulta = "INSERT INTO registro(estudiante, curso, materia, fecha, hora, estado) VALUES (%s, %s, %s,%s,%s,%s)"'''
    
    try:
        consulta = """
        INSERT INTO registro (estudiante, curso, materia, fecha, hora, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(consulta, (id_estudiante, curso , materia, fecha, hora, "Asistido"))
        connection.commit()
        print(f"Registro guardado:")
    except Exception as e:
        print(f"Error al guardar el registro: {e}")
    finally:
        cursor.close()
        connection.close()

            #BD de estudiantes'''

