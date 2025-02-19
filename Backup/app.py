import cv2
import face_recognition
from flask import Flask, Response, render_template, request, redirect, url_for, flash, session
from database import obtener_estudiantes, agregar_estudiante
from database import get_user_credentials
from database import *
#import pickle
import threading
from recognition import FaceRecognition


# Librerias para RF 
from flask import jsonify, Response

import numpy as np
import pandas as pd
from fpdf import FPDF
import io
#url_api = "http://127.0.0.1:5000/api/estudiantes"
app = Flask(__name__)
app.secret_key = "clave_secreta"

'''try:
    response = requests.get(url_api)
    response.raise_for_status()
    print("Conexión exitosa a la API. Datos obtenidos:")
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Error al conectar con la API: {e}")'''
@app.route("/")
def index():
    return render_template("index.html")
    #return render_template("index.html", cursos=cursos, materias=materias)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    # Verificar credenciales del usuario
    user = get_user_credentials(username)
    
    if user and user["password"] == password:
        session["user"] = user["username"]
        flash("Inicio de sesión exitoso", "success")
        return redirect(url_for("dashboard"))
    else:
        flash("Usuario o contraseña incorrectos", "danger")
        return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    else:
        flash("Por favor, inicie sesión primero", "warning")
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Sesión cerrada exitosamente", "info")
    return redirect(url_for("index"))

@app.route('/registro_asistencia', methods=['GET'])
def registro_asistencia():
    cursos = obtener_cursos()  # Función para obtener cursos desde la base de datos
    materias = obtener_materias()  # Función para obtener materias desde la base de datos
    #renderizar plantilla y pasar los datos. 
    #cursos = [
    #    {"id_curso": 1, "nombre_materia": "Matemáticas"},
     #   {"id_curso": 2, "nombre_materia": "Ciencias"},
     #   {"id_curso": 3, "nombre_materia": "Historia"}
    #]   
    return render_template('registro_asistencia.html', cursos=cursos, materias=materias)


#BD
# Base de datos simulada de estudiantes
KNOWN_FACES = [
    {
        "id": "6",
        "CI": "55555",
        "apellidos": "Andrade",
        "nombres": "Jose David",
        "curso": "1",
        "foto": "",
        "pff": "2",
        "name": "Alex",
        "image_path": "./static/faces/Alex.jpg"
    },
   {
        "name": "Sheimi",
        "image_path": "./static/faces/Sheimi.jpg"
   }
]


#Cargar las imágenes y codificaciones conocidas
known_face_encodings = []
known_face_names = []





#Lista de codificaciones de caras conocidas y nombres
#known_face_encodings = [
#    #Agrega codificaciones aquí, por ejemplo:
#    known_face_encodings(face_recognition.load_image_file("static/faces/Alex.jpg"))[0]
#]
#known_face_names = [
#   "Persona 1"
#]curso

for face in KNOWN_FACES:
    image = face_recognition.load_image_file(face["image_path"])
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)
    known_face_names.append(face["name"])

print(known_face_encodings)
print(known_face_names)

#@app.route('/control_asistencia', methods=['POST'])
#def control_asistencia():
#    curso_id = request.form.get('curso')
#    materia_id = request.form.get('materia')
#    # Aquí va la lógica para manejar el control de asistencia
#    return f"CONTROL DE ASISTENCIA realizado para Curso {curso_id} y Materia {materia_id}."

@app.route('/control_asistencia', methods=['POST'])
def control_asistencia():
    curso = request.form.get('curso')
    materia = request.form.get('materia')
    
    return render_template('control_facial.html', curso=curso, materia=materia)


@app.route('/video_feed')
def video_feed():
    """RUTA: Transmite el video en vivo."""
    return Response(gen_frames(known_face_encodings, known_face_names), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames1():
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not video_capture.isOpened():
        print("No se pudo abrir la cámara.")
        return
    
    try:
        while True:
            success, frame = video_capture.read()
            if not success:
                break

            # Redimensiona para mejorar el rendimiento
            #small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            if frame is None:
                print("No se está capturando el cuadro correctamente.")

            small_frame = cv2.resize(frame, (0, 0), fx=0.1, fy=0.1)  # Cambia de 0.25 a 0.5

            rgb_small_frame = small_frame[:, :, ::-1]  # Convertir a RGB

            # Detectar rostros en el cuadro reducido
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # Escalar las ubicaciones al tamaño original
            scaled_face_locations = [(top * 4, right * 4, bottom * 4, left * 4) 
                                      for (top, right, bottom, left) in face_locations]

            # Dibuja rectángulos y etiquetas en el cuadro original
            for (top, right, bottom, left) in scaled_face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Rostro", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        video_capture.release()


def gen_frames4():
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("No se pudo abrir la cámara.")
        return

    try:
        while True:
            success, frame = video_capture.read()
            if not success:
                break

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        video_capture.release()



def gen_frames(known_face_encodings, known_face_names): 
    """Captura video y realiza reconocimiento facial."""
    print("Iniciando captura de video...")
    estudiantes_diccionario=guardar_estudiantes_en_diccionario()
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        print("No se pudo acceder a la cámara.")
        return

    frame_skip = 5  # Procesa 1 de cada 'frame_skip' cuadros
    frame_count = 0
    
    try:
        while True:
            success, frame = video_capture.read()
            if not success:
                print("Error al leer el cuadro de la cámara.")
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            # Reducir el tamaño del cuadro para un procesamiento más rápido
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Detectar rostros y codificar
            face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
            '''image = face_recognition.load_image_file("static/faces/Alex.jpg")
            face_locations = face_recognition.face_locations(image)'''

            if face_locations:
                print("Se detecto rostro")
                #print(image)
                print(face_locations)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
            else:
                face_encodings = []
                print("No se detecto rostro")

            #face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # Escalar las ubicaciones al tamaño original
            scaled_face_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations]
            asistencia_registrada={}
            for (top, right, bottom, left), face_encoding in zip(scaled_face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Desconocido"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    # Verificar si el nombre ya está registrado en la sesión
                    ahora = datetime.now().date()
                    if name not in asistencia_registrada or asistencia_registrada[name] != ahora:
                        #obtener datos del estudiante desde el diccionario
                        estudiante=next((est for est in estudiantes_diccionario.values() if est['nombres'] == name), None)
                        if estudiante:
                            id_estudiante=estudiante['id_estudiante']
                            curso = estudiante['curso']
                            materia = estudiante['materia']
                            guardar_asistencia(id_estudiante, curso, materia)
                            asistencia_registrada[name] = ahora
                            #print(asistencia_registrada)
                        else:
                            print(f"No se encontró información para {name} en el diccionario.")
                    else:
                        print("Rostro no reconocido.")

                # Dibujar un rectángulo alrededor del rostro
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                # Etiquetar con el nombre
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            # Codificar la imagen a formato JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Enviar el marco como flujo continuo
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        video_capture.release()
        print("Captura de video finalizada.")



######################################## CODIGO PARA DOCENTE . funciones ################
# Ojo con esto, solo es para probar
estudiantes = []
asistencia = []
@app.route('/dashboard')
def docente_dashboard():
    return render_template('dashboard.html', estudiantes=estudiantes)

@app.route('/añadir_estudiante', methods=['POST'])
def añadir_estudiante():
    ci = request.form['ci']
    apellidos = request.form['apellidos']
    nombres = request.form['nombres']
    curso = request.form['curso']
    foto = request.form['foto']
    ppff= request.form['ppff']

    nuevo_estudiante = {"CI": ci, "Apellidos": apellidos, "Nombres": nombres, "Curso": curso, "Materia": foto, "PadreFamilia": ppff}
    estudiantes.append(nuevo_estudiante)
    return redirect(url_for('dashboard'))

@app.route('/generar_excel')
def generar_excel():
    df = pd.DataFrame(asistencia)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Asistencia')
    writer.save()
    output.seek(0)
    return send_file(output, attachment_filename="asistencia.xlsx", as_attachment=True)

@app.route('/generar_pdf')
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Registro de Asistencia", ln=True, align='C')
    
    # Encabezados
    pdf.cell(30, 10, "CI", 1)
    pdf.cell(50, 10, "Apellidos", 1)
    pdf.cell(50, 10, "Nombre", 1)
    pdf.cell(30, 10, "Curso", 1)
    pdf.cell(30, 10, "Materia", 1)
    pdf.ln()
    
    # Datos
    for registro in asistencia:
        pdf.cell(30, 10, registro["CI"], 1)
        pdf.cell(50, 10, registro["Apellidos"], 1)
        pdf.cell(50, 10, registro["Nombre"], 1)
        pdf.cell(30, 10, registro["Curso"], 1)
        pdf.cell(30, 10, registro["Materia"], 1)
        pdf.ln()
    
    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return send_file(output, attachment_filename="asistencia.pdf", as_attachment=True)

@app.route('/capture_attendance', methods=['GET'])
def capture_attendance():
    recognizer = FaceRecognition(faces_path="D:/Documentos/4_Maestria/Proyecto2/proyecto/static/faces")
    recognizer.recognize_faces()
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)

