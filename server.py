import socket
import sqlite3
from datetime import datetime


# CONFIGURACIÓN DEL SERVIDOR
# Datos que va a usar el servidor para conectarse

HOST = "localhost"
PORT = 5000
DB = "mensajes.db"



# BASE DE DATOS

# Aquí creamos la base de datos y la tabla donde se van a guardar los mensajes
def crear_db():
    """Crea la base de datos y la tabla si todavía no existen."""
    try:
        conexion = sqlite3.connect(DB)
        cursor = conexion.cursor()

        # Si la tabla no existe todavía, la crea automáticamente
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        """)

        # Guardamos los cambios hechos en la base
        conexion.commit()
        conexion.close()

        print("Base de datos creada correctamente.")

    except sqlite3.Error as error:
        print("Error al acceder a la base de datos:", error)

# Acá guardamos cada mensaje que llega con lo que solicitamos en este caso contenido, fecha y la ip del cliente que lo envió.
def guardar_mensaje(contenido, fecha, ip_cliente):
    """Guarda el mensaje recibido."""


# Agregamos el mensaje recibido a la tabla mensajes de nuestra base de datos. Si hay un error, lo mostramos.
    try:
        conexion = sqlite3.connect(DB)
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
            VALUES (?, ?, ?)
        """, (contenido, fecha, ip_cliente))

        conexion.commit()
        conexion.close()

    except sqlite3.Error as error:
        print("Error al guardar el mensaje:", error)



# SOCKET DEL SERVIDOR

# Creamos el socket que va a esperar la conexión del cliente
def crear_servidor():
    """Crea y configura el socket del servidor."""

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        servidor.bind((HOST, PORT))
        servidor.listen()

        print(f"Servidor escuchando en {HOST}:{PORT}...")

        return servidor

# Si el puerto ya está ocupado, mostramos el problema
    except OSError as error:
        print("No se pudo iniciar el servidor.")
        print("Puede ser que el puerto esté ocupado.")
        print("Error:", error)

        servidor.close()

        return None



# RECIBIR MENSAJES

#Aquí recibimos los mensajes que envía el cliente y lo guardamos en la DB.
def atender_cliente(conn, addr):

    ip_cliente = addr[0]

    print(f"\nCliente conectado desde {ip_cliente}")

    while True:

        try:
            mensaje = conn.recv(1024).decode("utf-8")

            if not mensaje:
                break

            print(f"Mensaje recibido: {mensaje}")


            # Guardamos la fecha y hora exacta en la que llegó el mensaje
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            guardar_mensaje(mensaje, fecha, ip_cliente)

            respuesta = f"Mensaje recibido: {fecha}"

            conn.sendall(respuesta.encode("utf-8"))

        except ConnectionError:
            print("Se perdió la conexión con el cliente.")
            break

    print("Cliente desconectado.")



# P. PRINCIPAL

# Primero preparamos la base y después ponemos en marcha el servidor
def ejecutar_servidor():

    crear_db()

    servidor = crear_servidor()

    if servidor is None:
        return

    try:

        while True:

            print("\nEsperando conexión...")

            conn, addr = servidor.accept()

            with conn:
                atender_cliente(conn, addr)

    except KeyboardInterrupt:
        print("\nServidor detenido.")

    finally:
        servidor.close()

# Aquí hacemos que el servidor arranque cuando ejecutamos este archivo
if __name__ == "__main__":
    ejecutar_servidor()