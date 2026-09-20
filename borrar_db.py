# Creé este archivo aparte para poder borrar los mensajes de la base
# Surgio la necesidad debido a que quería dejar limpia la bd para poder hacer otras pruebas

# Aclaración: se borran todos los mensajes, no uno solo.
import sqlite3

conexion = sqlite3.connect("mensajes.db")
cursor = conexion.cursor()

# Se borran todos los registros guardados en la tabla mensajes
cursor.execute("DELETE FROM mensajes")

# Guardamos los cambios y cerramos la conexión
conexion.commit()
conexion.close()

print("Todos los mensajes fueron eliminados.")