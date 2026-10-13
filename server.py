import os
import secrets
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, session
from werkzeug.security import check_password_hash, generate_password_hash


# CONFIGURACIÓN DEL SERVIDOR
HOST = "localhost"
PORT = 5000
DB = Path(__file__).with_name("tareas.db")
app = Flask(__name__)
# Para pruebas locales, la clave cambia al reiniciar si no hay variable de entorno.
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# BASE DE DATOS
def conectar_db():
    conexion = sqlite3.connect(DB)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def crear_db():
    """Crea las tablas si todavía no existen."""
    conexion = conectar_db()
    try:
        conexion.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            contraseña TEXT NOT NULL
        )''')
        conexion.execute('''CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            completada INTEGER NOT NULL DEFAULT 0,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id)
        )''')
        conexion.commit()
    finally:
        conexion.close()


def leer_datos():
    datos = request.get_json(silent=True)
    if isinstance(datos, dict):
        return datos
    return {}


def leer_texto(datos, campo):
    valor = datos.get(campo)
    if isinstance(valor, str):
        return valor
    return ""


# REGISTRO Y SESIONES
@app.post("/registro")
def registrar_usuario():
    datos = leer_datos()
    usuario = leer_texto(datos, "usuario").strip()
    contraseña = leer_texto(datos, "contraseña")
    if not usuario or not contraseña.strip():
        return jsonify(mensaje="Completá el usuario y la contraseña."), 400
    contraseña_hash = generate_password_hash(contraseña)
    conexion = conectar_db()
    try:
        conexion.execute(
            "INSERT INTO usuarios (usuario, contraseña) VALUES (?, ?)",
            (usuario, contraseña_hash),
        )
        conexion.commit()
    except sqlite3.IntegrityError:
        return jsonify(mensaje="Ese usuario ya existe."), 409
    finally:
        conexion.close()
    return jsonify(mensaje="Usuario registrado correctamente."), 201


@app.post("/login")
def iniciar_sesion():
    datos = leer_datos()
    usuario = leer_texto(datos, "usuario").strip()
    contraseña = leer_texto(datos, "contraseña")
    conexion = conectar_db()
    try:
        registro = conexion.execute(
            "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()
    finally:
        conexion.close()
    if registro is None or not check_password_hash(registro["contraseña"], contraseña):
        return jsonify(mensaje="Usuario o contraseña incorrectos."), 401
    session.clear()
    session["usuario_id"] = registro["id"]
    session["usuario"] = registro["usuario"]
    return jsonify(mensaje="Sesión iniciada.")


@app.post("/logout")
def cerrar_sesion():
    session.clear()
    return jsonify(mensaje="Sesión cerrada.")


@app.get("/tareas")
def mostrar_bienvenida():
    return render_template_string('''<!doctype html>
        <html lang="es">
        <head><meta charset="utf-8"><title>Mis tareas</title></head>
        <body><h1>Sistema de Gestión de Tareas</h1>
        {% if usuario %}
            <p>Bienvenido/a, {{ usuario }}.</p>
            <p>Podés administrar tus tareas desde el cliente de consola.</p>
        {% else %}
            <p>Necesitás iniciar sesión primero.</p>
        {% endif %}
        </body></html>''', usuario=session.get("usuario"))


@app.before_request
def verificar_sesion():
    if request.path.startswith("/api/tareas") and "usuario_id" not in session:
        return jsonify(mensaje="Necesitás iniciar sesión primero."), 401


# GESTIÓN DE TAREAS
@app.get("/api/tareas")
def consultar_tareas():
    conexion = conectar_db()
    try:
        tareas = conexion.execute(
            "SELECT id, descripcion, completada FROM tareas WHERE usuario_id = ? ORDER BY id",
            (session["usuario_id"],),
        ).fetchall()
    finally:
        conexion.close()
    return jsonify(tareas=[dict(tarea) for tarea in tareas])


@app.post("/api/tareas")
def agregar_tarea():
    descripcion = leer_texto(leer_datos(), "descripcion").strip()
    if not descripcion:
        return jsonify(mensaje="La descripción no puede estar vacía."), 400
    conexion = conectar_db()
    try:
        cursor = conexion.execute(
            "INSERT INTO tareas (descripcion, usuario_id) VALUES (?, ?)",
            (descripcion, session["usuario_id"]),
        )
        conexion.commit()
        tarea_id = cursor.lastrowid
    finally:
        conexion.close()
    return jsonify(mensaje="Tarea agregada correctamente.", id=tarea_id), 201


@app.put("/api/tareas/<int:tarea_id>")
def completar_tarea(tarea_id):
    conexion = conectar_db()
    try:
        cursor = conexion.execute(
            "UPDATE tareas SET completada = 1 WHERE id = ? AND usuario_id = ?",
            (tarea_id, session["usuario_id"]),
        )
        conexion.commit()
        modificadas = cursor.rowcount
    finally:
        conexion.close()
    if modificadas == 0:
        return jsonify(mensaje="Tarea no encontrada."), 404
    return jsonify(mensaje="Tarea completada.")


@app.delete("/api/tareas/<int:tarea_id>")
def eliminar_tarea(tarea_id):
    conexion = conectar_db()
    try:
        cursor = conexion.execute(
            "DELETE FROM tareas WHERE id = ? AND usuario_id = ?",
            (tarea_id, session["usuario_id"]),
        )
        conexion.commit()
        eliminadas = cursor.rowcount
    finally:
        conexion.close()
    if eliminadas == 0:
        return jsonify(mensaje="Tarea no encontrada."), 404
    return jsonify(mensaje="Tarea eliminada.")


@app.errorhandler(sqlite3.Error)
def error_base_datos(error):
    app.logger.error("Error de SQLite: %s", error)
    return jsonify(mensaje="No se pudo acceder a la base de datos."), 500


def ejecutar_servidor():
    crear_db()
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    ejecutar_servidor()
