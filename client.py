import socket


# CONFIGURACIÓN DEL CLIENTE

# Datos del servidor al que nos queremos conectar
HOST = "localhost"
PORT = 5000


def iniciar_cliente():

    # Creamos el socket que va a usar el cliente
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:

        try:

            cliente.connect((HOST, PORT))

            print(f"Conectado al servidor {HOST}:{PORT}")
            print("Escribí 'éxito' para finalizar.\n")

            # # Lo usamos para saber cuántos mensajes mandamos durante la conexión
            contador = 0


            # El cliente puede seguir mandando mensajes hasta escribir éxito para terminar la conexión.
            while True:

                mensaje = input("Escribí un mensaje: ")

                
                if mensaje.lower() in ["éxito", "exito"]:
                    print("\nConexión finalizada.")
                    print(f"Total de mensajes enviados: {contador}")
                    break

                # Evitar mensajes vacíos
                if mensaje.strip() == "":
                    print("El mensaje no puede estar vacío.\n")
                    continue

                # Enviar mensaje
                cliente.sendall(mensaje.encode("utf-8"))

                # Recibir respuesta y sumar 1 al contador
                respuesta = cliente.recv(1024).decode("utf-8")
                contador += 1

                print(f"Servidor: {respuesta}")
                print(f"Mensaje número {contador} enviado correctamente.\n")

        # Este error aparece si intentamos entrar y el servidor todavía no está iniciado
        except ConnectionRefusedError:
            print("No se pudo conectar con el servidor.")
            print("Asegurate de ejecutar primero server.py.")

        except ConnectionError:
            print("Se perdió la conexión con el servidor.")


if __name__ == "__main__":
    iniciar_cliente()