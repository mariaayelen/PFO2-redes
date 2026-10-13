

import requests


# CONFIGURACIÓN DEL CLIENTE
URL = "http://localhost:5000"


def enviar_solicitud(cliente, metodo, ruta, datos=None):
    """Envía la solicitud y controla los errores más comunes."""
    try:
        respuesta = cliente.request(metodo, URL + ruta, json=datos, timeout=10)
        contenido = respuesta.json()
        if not isinstance(contenido, dict):
            print("El servidor devolvió una respuesta inesperada.")
            return None
        if "mensaje" in contenido:
            print(contenido["mensaje"])
        return respuesta
    except requests.exceptions.Timeout:
        print("El servidor tardó demasiado en responder.")
    except requests.exceptions.ConnectionError:
        print("No se pudo conectar con el servidor.")
        print("Asegurate de ejecutar primero server.py.")
    except requests.exceptions.RequestException:
        print("No se pudo completar la solicitud.")
    except ValueError:
        print("El servidor devolvió una respuesta inesperada.")
    return None


def pedir_usuario():
    usuario = input("Usuario: ").strip()
    contraseña = input("Contraseña: ")
    return {"usuario": usuario, "contraseña": contraseña}


def ver_tareas(respuesta):
    tareas = respuesta.json().get("tareas")
    if not isinstance(tareas, list):
        print("El servidor devolvió una respuesta inesperada.")
        return
    if not tareas:
        print("No tenés tareas guardadas.")
    for tarea in tareas:
        estado = "Completada" if tarea["completada"] else "Pendiente"
        print(f'{tarea["id"]}. {tarea["descripcion"]} - {estado}')


def menu_tareas(cliente):
    while True:
        print("\n=== MIS TAREAS ===\n")
        print("1. Ver mis tareas\n2. Agregar tarea\n3. Completar tarea")
        print("4. Eliminar tarea\n5. Cerrar sesión")
        opcion = input("\nElegí una opción: ").strip()
        respuesta = None
        if opcion == "1":
            respuesta = enviar_solicitud(cliente, "GET", "/api/tareas")
            if respuesta is not None and respuesta.status_code == 200:
                ver_tareas(respuesta)
        elif opcion == "2":
            descripcion = input("Descripción: ").strip()
            if not descripcion:
                print("La descripción no puede estar vacía.")
                continue
            respuesta = enviar_solicitud(
                cliente, "POST", "/api/tareas", {"descripcion": descripcion}
            )
        elif opcion in ["3", "4"]:
            try:
                tarea_id = int(input("ID de la tarea: "))
                if tarea_id <= 0:
                    raise ValueError
            except ValueError:
                print("Ingresá un ID numérico mayor que cero.")
                continue
            metodo = "PUT" if opcion == "3" else "DELETE"
            respuesta = enviar_solicitud(cliente, metodo, f"/api/tareas/{tarea_id}")
        elif opcion == "5":
            respuesta = enviar_solicitud(cliente, "POST", "/logout")
            if respuesta is not None and respuesta.status_code == 200:
                return
        else:
            print("Elegí una opción válida.")
        if respuesta is not None and respuesta.status_code == 401:
            cliente.cookies.clear()
            return


def iniciar_cliente():
    # La sesión conserva las cookies entre las solicitudes.
    with requests.Session() as cliente:
        try:
            while True:
                print("\n=== SISTEMA DE GESTIÓN DE TAREAS ===\n")
                print("1. Registrarse\n2. Iniciar sesión\n0. Salir")
                opcion = input("\nElegí una opción: ").strip()
                if opcion == "1":
                    enviar_solicitud(cliente, "POST", "/registro", pedir_usuario())
                elif opcion == "2":
                    respuesta = enviar_solicitud(cliente, "POST", "/login", pedir_usuario())
                    if respuesta is not None and respuesta.status_code == 200:
                        menu_tareas(cliente)
                elif opcion == "0":
                    print("Hasta luego.")
                    break
                else:
                    print("Elegí una opción válida.")
        except (KeyboardInterrupt, EOFError):
            print("\nCliente finalizado.")


if __name__ == "__main__":
    iniciar_cliente()
